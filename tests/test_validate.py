"""Integration tests for session validation (/auth/validate)."""
from tests.conftest import make_basic_auth_header


def test_validate_with_valid_session_cookie(client):
    """After login, /auth/validate returns 200."""
    # Login first to get session cookie
    client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'testuser',
        'target': '/'
    })

    # Validate with the session cookie (automatically sent by test client)
    resp = client.get('/auth/validate')
    assert resp.status_code == 200
    assert b'session verified' in resp.data.lower()


def test_validate_without_cookie_returns_401(client):
    """GET /auth/validate without session cookie returns 401."""
    resp = client.get('/auth/validate')
    assert resp.status_code == 401
    assert 'WWW-Authenticate' in resp.headers
    assert 'Basic realm=' in resp.headers['WWW-Authenticate']


def test_validate_with_valid_basic_auth(client):
    """GET /auth/validate with valid Basic Auth returns 200 and sets cookies."""
    resp = client.get('/auth/validate', headers={
        'Authorization': make_basic_auth_header('testuser', 'testuser')
    })
    assert resp.status_code == 200
    assert b'verified' in resp.data.lower()

    # Should also set cookies for future requests
    assert client.get_cookie('auth_session') is not None
    assert client.get_cookie('auth_access_token') is not None


def test_validate_with_invalid_basic_auth(client):
    """GET /auth/validate with invalid Basic Auth returns 401."""
    resp = client.get('/auth/validate', headers={
        'Authorization': make_basic_auth_header('testuser', 'wrongpassword')
    })
    assert resp.status_code == 401
    assert 'WWW-Authenticate' in resp.headers
