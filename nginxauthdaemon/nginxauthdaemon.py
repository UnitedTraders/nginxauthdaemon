import base64
import importlib
from flask import Flask
from flask import render_template, request, make_response, redirect, g
from Crypto.Cipher import DES


app = Flask(__name__)
app.config.from_object('config.DefaultConfig')
app.config.from_envvar('DAEMON_SETTINGS', True)


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
        auth_decoded = base64.b64decode(auth_value)
        return auth_decoded.split(':', 2)
    except TypeError, e:
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
    des = DES.new(app.config['DES_KEY'], DES.MODE_ECB, app.config['DES_IV'])
    clear_text = username + app.config['SESSION_SALT']
    if len(clear_text) % 8 != 0:
        clear_text = clear_text.ljust((len(clear_text) / 8 + 1) * 8, ' ')
    return base64.encodestring(des.encrypt(clear_text))


def decode_session_cookie(cookie):
    """Decode session cookie and return user name"""
    try:
        encrypted = base64.decodestring(cookie)
        des = DES.new(app.config['DES_KEY'], DES.MODE_ECB, app.config['DES_IV'])
        decrypted = des.decrypt(encrypted).rstrip()
        session_salt = app.config['SESSION_SALT']
        if decrypted[-len(session_salt):] == session_salt:
            return decrypted[:-len(session_salt)]
        return None
    except:
        return None


@app.route('/auth/login', methods=['GET', 'POST'])
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
            resp.set_cookie(app.config['SESSION_COOKIE'], create_session_cookie(username))
            return resp
        else:
            return render_template('login.html', realm=app.config['REALM_NAME'], error="Please check user name and password")


@app.route('/auth/validate', methods=['GET'])
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
        resp.set_cookie(app.config['SESSION_COOKIE'], create_session_cookie(user_and_password[0]))
        return resp
    else:
        resp = make_response("Username/password failed", 401)
        resp.headers['WWW-Authenticate'] = 'Basic realm=' + app.config['REALM_NAME']
        resp.headers['Cache-Control'] = 'no-cache'
        return resp


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
