import base64
import time
import uuid
import importlib
from flask import Flask
from flask import render_template, request, make_response, redirect, g
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import jwt

BLOCK_SIZE = 32 # Bytes
cookies_max_age = 7 * 24 * 60 * 60 # 1week

app = Flask(__name__)
app.config.from_object('nginxauthdaemon.config.DefaultConfig')
app.config.from_envvar('DAEMON_SETTINGS', True)
custom_auth_url_prefix=app.config['AUTH_URL_PREFIX']

def get_authenticator():
    auth = getattr(g, '_authenticator', None)
    if auth is None:
        class_name = app.config['AUTHENTICATOR']
        parts = class_name.split('.')
        module = importlib.import_module(".".join(parts[:-1]))
        cls = getattr(module, parts[-1])
        auth = g._authenticator = cls(app.config)
    return auth


def decode_basic(auth_value):
    if auth_value is None or auth_value == '':
        return None

    try:
        auth_decoded = base64.b64decode(auth_value).decode("utf-8")
        return auth_decoded.split(':', 2)
    except TypeError as e:
        app.logger.warn("Parsing decoded basic value %s failed. Value ignored" % auth_value, e)
        return None


def parse_authorization(original_value):
    """Parse 'Authorization' header and return (user, password) tuple for success and None for failure."""
    if original_value is None:
        return None
    if original_value.startswith("Basic "):
        return decode_basic(original_value[6:])
    app.logger.warn("Ignored unsupported authorization header %s" % original_value)
    return None


def create_session_cookie(username):
    """Create session cookie. Returns string"""
    des = DES.new(bytes(app.config['DES_KEY'], encoding="raw_unicode_escape"), DES.MODE_ECB)
    clear_text = username + app.config['SESSION_SALT']
    return base64.encodestring(des.encrypt(pad(clear_text.encode('utf-8'), BLOCK_SIZE)))

def create_access_token_cookie(username):
    """Create access token. Returns string"""
    jwtPrivateKey = app.config['JWT_PRIVATE_KEY']

    now = int(time.time()) 
    expiresAt = now + cookies_max_age # seconds
    payload = {'jti': str(uuid.uuid4()), 'iat': now, 'nbf': 0, 'iss': 'realm://crowd-ldap', 'real-issuer': 'crowd-ldap', 'exp': expiresAt, 'realm_access': {'roles': []}, 'user_id': username, 'typ': 'Bearer'}

    return jwt.encode(payload, jwtPrivateKey, algorithm='RS256')

def decode_session_cookie(cookie):
    """Decode session cookie and return user name"""
    try:
        encrypted = base64.decodestring(bytes(cookie,'utf-8'))
        des = DES.new(bytes(app.config['DES_KEY'], encoding="raw_unicode_escape"), DES.MODE_ECB)
        decrypted = unpad(des.decrypt(encrypted).rstrip(), BLOCK_SIZE)
        session_salt = app.config['SESSION_SALT']
        if decrypted[-len(session_salt):].decode("utf-8") == session_salt:
            return decrypted[:-len(session_salt)]
        return None
    except:
        return None


@app.route(custom_auth_url_prefix +'/login', methods=['GET', 'POST'])
def show_login():
    if request.method == 'GET':
        target = request.headers.get(app.config['TARGET_HEADER'])
        return render_template('login.html', realm=app.config['REALM_NAME'], target=target)
    else:
        # check user name and password
        username = request.form.get('user')
        password = request.form.get('pass')
        target = request.form.get('target')
        if username is not None and get_authenticator().authenticate(username, password):
            resp = redirect(target)
            if target == custom_auth_url_prefix +'/login':
                resp = redirect("/")
            resp.set_cookie(app.config['SESSION_COOKIE'], create_session_cookie(username), max_age=cookies_max_age)
            resp.set_cookie(app.config['ACCESS_TOKEN_COOKIE'], create_access_token_cookie(username), max_age=cookies_max_age)
            return resp
        else:
            return render_template('login.html', realm=app.config['REALM_NAME'], error="Please check user name and password"), 401


@app.route(custom_auth_url_prefix +'/validate', methods=['GET'])
def validate():
    # check session
    session_cookie = request.cookies.get(app.config['SESSION_COOKIE'])
    if session_cookie is not None:
        username = decode_session_cookie(session_cookie)
        if username is not None:
            # seems username is right
            return "Session verified"

    # check Authorization header
    user_and_password = request.headers.get('Authorization', type=parse_authorization)
    if user_and_password is None:
        # neither header nor cookie fits, return 401
        resp = make_response('Unauthorized', 401)
        resp.headers['WWW-Authenticate'] = 'Basic realm=' + app.config['REALM_NAME']
        resp.headers['Cache-Control'] = 'no-cache'
        return resp

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


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
