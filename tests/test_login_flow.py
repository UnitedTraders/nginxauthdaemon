"""Integration tests for login flow (/auth/login)."""


def test_login_page_renders(client):
    """GET /auth/login returns the login form."""
    resp = client.get('/auth/login', headers={'X-Target': '/protected'})
    assert resp.status_code == 200
    assert b'login' in resp.data.lower()


def test_login_success_sets_cookies_and_redirects(client):
    """POST valid credentials sets session + access token cookies and redirects."""
    resp = client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'testuser',
        'target': '/protected/page'
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/protected/page'

    # Check cookies were set
    assert client.get_cookie('auth_session') is not None
    assert client.get_cookie('auth_access_token') is not None


def test_login_failure_returns_401_no_cookies(client):
    """POST invalid credentials returns 401 and does not set cookies."""
    resp = client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'wrongpassword',
        'target': '/protected'
    })
    assert resp.status_code == 401
    assert b'check user name and password' in resp.data.lower()

    # No session cookie should be set
    assert client.get_cookie('auth_session') is None


def test_login_redirects_to_target(client):
    """Successful login redirects to the specified target URL."""
    resp = client.post('/auth/login', data={
        'user': 'admin',
        'pass': 'admin',
        'target': '/dashboard/overview'
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/dashboard/overview'


def test_login_with_login_target_redirects_to_root(client):
    """If target is the login page itself, redirect to root."""
    resp = client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'testuser',
        'target': '/auth/login'
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/'
