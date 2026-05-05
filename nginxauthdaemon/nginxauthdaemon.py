import base64
import sys
import time
import uuid
import importlib
from flask import Flask
from flask import render_template, request, make_response, redirect, g, current_app
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import jwt
from pydantic import ValidationError

from nginxauthdaemon.config import load_config, AUTHENTICATOR_MAP

BLOCK_SIZE = 32  # Bytes
cookies_max_age = 7 * 24 * 60 * 60  # 1week


def get_authenticator():
    auth = getattr(g, '_authenticator', None)
    if auth is None:
        from flask import current_app
        class_path = current_app.config['AUTHENTICATOR_CLASS']
        parts = class_path.split('.')
        module = importlib.import_module(".".join(parts[:-1]))
        cls = getattr(module, parts[-1])
        auth = g._authenticator = cls(current_app.config)
        return auth
    return auth


def decode_basic(auth_value):
    if auth_value is None or auth_value == '':
        return None

    try:
        auth_decoded = base64.b64decode(auth_value).decode("utf-8")
        return auth_decoded.split(':', 2)
    except TypeError as e:
        from flask import current_app
        current_app.logger.warn("Parsing decoded basic value %s failed. Value ignored" % auth_value, e)
        return None


def parse_authorization(original_value):
    """Parse 'Authorization' header and return (user, password) tuple for success and None for failure."""
    if original_value is None:
        return None
    if original_value.startswith("Basic "):
        return decode_basic(original_value[6:])
    from flask import current_app
    current_app.logger.warn("Ignored unsupported authorization header %s" % original_value)
    return None


def create_session_cookie(username):
    """Create session cookie. Returns string"""
    from flask import current_app
    des = DES.new(current_app.config['DES_KEY_BYTES'], DES.MODE_ECB)
    clear_text = username + current_app.config['SESSION_SALT']
    return base64.b64encode(des.encrypt(pad(clear_text.encode('utf-8'), BLOCK_SIZE))).decode('ascii')


def create_access_token_cookie(username):
    """Create access token. Returns string"""
    from flask import current_app
    jwtPrivateKey = current_app.config['JWT_PRIVATE_KEY']

    now = int(time.time())
    expiresAt = now + cookies_max_age  # seconds
    payload = {'jti': str(uuid.uuid4()), 'iat': now, 'nbf': 0, 'iss': 'realm://crowd-ldap', 'real-issuer': 'crowd-ldap', 'exp': expiresAt, 'realm_access': {'roles': []}, 'user_id': username, 'typ': 'Bearer'}

    return jwt.encode(payload, jwtPrivateKey, algorithm='RS256')


def decode_session_cookie(cookie):
    """Decode session cookie and return user name"""
    from flask import current_app
    try:
        encrypted = base64.b64decode(bytes(cookie, 'utf-8'))
        des = DES.new(current_app.config['DES_KEY_BYTES'], DES.MODE_ECB)
        decrypted = unpad(des.decrypt(encrypted), BLOCK_SIZE)
        session_salt = current_app.config['SESSION_SALT']
        if decrypted[-len(session_salt):].decode("utf-8") == session_salt:
            return decrypted[:-len(session_salt)]
        return None
    except Exception:
        return None


def create_app(config_path=None):
    """Create and configure the Flask application.

    Args:
        config_path: Path to TOML config file. If None, reads from
                     DAEMON_SETTINGS environment variable.

    Returns:
        Configured Flask application.

    Raises:
        SystemExit: If configuration validation fails.
    """
    try:
        config = load_config(config_path)
    except ValidationError as e:
        print("Configuration error:", file=sys.stderr)
        for error in e.errors():
            loc = '.'.join(str(l) for l in error['loc'])
            print(f"  - {loc}: {error['msg']}", file=sys.stderr)
        sys.exit(1)

    app = Flask(__name__)
    app.config.update(config.to_flask_config())

    auth_url_prefix = app.config['AUTH_URL_PREFIX']

    @app.route(auth_url_prefix + '/login', methods=['GET', 'POST'])
    def show_login():
        if request.method == 'GET':
            target = request.headers.get(app.config['TARGET_HEADER'])
            return render_template('login.html', realm=app.config['REALM_NAME'], target=target)
        else:
            username = request.form.get('user')
            password = request.form.get('pass')
            target = request.form.get('target')
            try:
                if username is not None and get_authenticator().authenticate(username, password):
                    resp = redirect(target)
                    if target == auth_url_prefix + '/login':
                        resp = redirect("/")
                    resp.set_cookie(app.config['SESSION_COOKIE'], create_session_cookie(username), max_age=cookies_max_age)
                    resp.set_cookie(app.config['ACCESS_TOKEN_COOKIE'], create_access_token_cookie(username), max_age=cookies_max_age)
                    return resp
                else:
                    return render_template('login.html', realm=app.config['REALM_NAME'], error="Please check user name and password"), 401
            except Exception:
                current_app.logger.exception("Authentication backend error during login")
                return render_template('login.html', realm=app.config['REALM_NAME'], error="Authentication service is temporarily unavailable. Please try again later."), 503

    @app.route(auth_url_prefix + '/validate', methods=['GET'])
    def validate():
        session_cookie = request.cookies.get(app.config['SESSION_COOKIE'])
        if session_cookie is not None:
            username = decode_session_cookie(session_cookie)
            if username is not None:
                return "Session verified"

        user_and_password = request.headers.get('Authorization', type=parse_authorization)
        if user_and_password is None:
            resp = make_response('Unauthorized', 401)
            resp.headers['WWW-Authenticate'] = 'Basic realm=' + app.config['REALM_NAME']
            resp.headers['Cache-Control'] = 'no-cache'
            return resp

        try:
            if get_authenticator().authenticate(user_and_password[0], user_and_password[1]):
                resp = make_response("Username/password verified")
                username = user_and_password[0]
                resp.set_cookie(app.config['SESSION_COOKIE'], create_session_cookie(username), max_age=cookies_max_age)
                resp.set_cookie(app.config['ACCESS_TOKEN_COOKIE'], create_access_token_cookie(username), max_age=cookies_max_age)
                return resp
            else:
                resp = make_response("Username/password failed", 401)
                resp.headers['WWW-Authenticate'] = 'Basic realm=' + app.config['REALM_NAME']
                resp.headers['Cache-Control'] = 'no-cache'
                return resp
        except Exception:
            current_app.logger.exception("Authentication backend error during validation")
            resp = make_response("Authentication service unavailable", 503)
            resp.headers['Cache-Control'] = 'no-cache'
            return resp

    return app


if __name__ == '__main__':
    application = create_app()
    application.run('localhost', 5000, debug=True)
