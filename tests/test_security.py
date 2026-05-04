"""Integration tests for security properties (encryption, tamper detection, JWT)."""
import pytest
import jwt as pyjwt
from tests.conftest import make_basic_auth_header


def test_tampered_cookie_is_rejected(client, app):
    """A cookie with modified bytes is rejected by /auth/validate."""
    # Login to get a valid cookie
    client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'testuser',
        'target': '/'
    })

    # Get the session cookie value and tamper with it
    cookie = client.get_cookie('auth_session')
    assert cookie is not None
    session_value = cookie.value

    # Tamper: flip some characters in the base64 payload
    tampered = session_value[:-4] + 'XXXX'

    # Clear cookies and set tampered one
    client.delete_cookie('auth_session')
    client.set_cookie('auth_session', tampered, domain='localhost')

    resp = client.get('/auth/validate')
    assert resp.status_code == 401


def test_cookie_with_wrong_des_key_is_rejected(client, app):
    """A cookie encrypted with a different DES key is rejected."""
    import base64
    from Crypto.Cipher import DES
    from Crypto.Util.Padding import pad

    BLOCK_SIZE = 32
    # Use a different DES key than the app's configured key
    wrong_key = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    des = DES.new(wrong_key, DES.MODE_ECB)
    clear_text = 'testuser' + app.config['SESSION_SALT']
    fake_cookie = base64.encodebytes(
        des.encrypt(pad(clear_text.encode('utf-8'), BLOCK_SIZE))
    ).decode()

    client.set_cookie('auth_session', fake_cookie, domain='localhost')

    resp = client.get('/auth/validate')
    assert resp.status_code == 401


def test_cookie_with_wrong_salt_is_rejected(client, app):
    """A cookie with the wrong salt suffix is rejected."""
    import base64
    from Crypto.Cipher import DES
    from Crypto.Util.Padding import pad

    BLOCK_SIZE = 32
    des_key = bytes(app.config['DES_KEY'], encoding="raw_unicode_escape")
    des = DES.new(des_key, DES.MODE_ECB)
    # Use wrong salt
    clear_text = 'testuser' + 'WRONG_SALT_VALUE'
    fake_cookie = base64.encodebytes(
        des.encrypt(pad(clear_text.encode('utf-8'), BLOCK_SIZE))
    ).decode()

    client.set_cookie('auth_session', fake_cookie, domain='localhost')

    resp = client.get('/auth/validate')
    assert resp.status_code == 401


def test_jwt_access_token_contains_expected_claims(client, public_key):
    """JWT access token contains user_id, exp, and is RS256-signed."""
    # Login to get JWT
    client.post('/auth/login', data={
        'user': 'jwtuser',
        'pass': 'jwtuser',
        'target': '/'
    })

    # Extract JWT cookie
    cookie = client.get_cookie('auth_access_token')
    assert cookie is not None
    jwt_value = cookie.value

    # Decode and verify claims
    decoded = pyjwt.decode(
        jwt_value,
        public_key,
        algorithms=['RS256']
    )
    assert decoded['user_id'] == 'jwtuser'
    assert 'exp' in decoded
    assert 'iat' in decoded
    assert decoded['typ'] == 'Bearer'


def test_jwt_with_wrong_algorithm_fails(client, public_key):
    """JWT verification fails if algorithm doesn't match."""
    # Login to get JWT
    client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'testuser',
        'target': '/'
    })

    cookie = client.get_cookie('auth_access_token')
    assert cookie is not None
    jwt_value = cookie.value

    # Attempting to decode with HS256 should fail
    with pytest.raises(pyjwt.exceptions.InvalidAlgorithmError):
        pyjwt.decode(jwt_value, public_key, algorithms=['HS256'])
