"""Integration tests for CrowdAuthenticator (mocked Crowd server)."""
from unittest.mock import patch, MagicMock
import pytest
from nginxauthdaemon.crowdauth import CrowdAuthenticator


@pytest.fixture
def crowd_config():
    """Minimal config for CrowdAuthenticator."""
    return {
        'CROWD_URL': 'http://crowd.example.com/crowd/',
        'CROWD_APP_NAME': 'testapp',
        'CROWD_APP_PASSWORD': 'testpass',
    }


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_auth_success(mock_crowd_class, crowd_config):
    """CrowdAuthenticator returns True when Crowd confirms the user."""
    mock_server = MagicMock()
    mock_server.auth_user.return_value = {'name': 'alice'}
    mock_crowd_class.return_value = mock_server

    auth = CrowdAuthenticator(crowd_config)
    assert auth.authenticate('alice', 'correctpassword') is True

    mock_server.auth_user.assert_called_once_with('alice', 'correctpassword')


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_auth_failure_returns_none(mock_crowd_class, crowd_config):
    """CrowdAuthenticator returns False when Crowd returns None (bad credentials)."""
    mock_server = MagicMock()
    mock_server.auth_user.return_value = None
    mock_crowd_class.return_value = mock_server

    auth = CrowdAuthenticator(crowd_config)
    assert auth.authenticate('alice', 'wrongpassword') is False


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_auth_username_mismatch(mock_crowd_class, crowd_config):
    """CrowdAuthenticator returns False when Crowd returns a different username."""
    mock_server = MagicMock()
    mock_server.auth_user.return_value = {'name': 'bob'}
    mock_crowd_class.return_value = mock_server

    auth = CrowdAuthenticator(crowd_config)
    assert auth.authenticate('alice', 'password') is False


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_authenticator_initializes_with_config(mock_crowd_class, crowd_config):
    """CrowdAuthenticator passes URL, app name, and password to CrowdServer."""
    CrowdAuthenticator(crowd_config)

    mock_crowd_class.assert_called_once_with(
        'http://crowd.example.com/crowd/',
        'testapp',
        'testpass',
    )


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_auth_via_login_endpoint(mock_crowd_class, client, app):
    """Full login flow with CrowdAuthenticator via /auth/login."""
    mock_server = MagicMock()
    mock_server.auth_user.return_value = {'name': 'crowduser'}
    mock_crowd_class.return_value = mock_server

    app.config.update({
        'AUTHENTICATOR': 'nginxauthdaemon.crowdauth.CrowdAuthenticator',
        'CROWD_URL': 'http://crowd.example.com/crowd/',
        'CROWD_APP_NAME': 'testapp',
        'CROWD_APP_PASSWORD': 'testpass',
    })

    resp = client.post('/auth/login', data={
        'user': 'crowduser',
        'pass': 'crowdpass',
        'target': '/dashboard'
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/dashboard'
    assert client.get_cookie('auth_session') is not None
    assert client.get_cookie('auth_access_token') is not None

    # Reset
    app.config['AUTHENTICATOR'] = 'nginxauthdaemon.auth.DummyAuthenticator'


@patch('nginxauthdaemon.crowdauth.crowd.CrowdServer')
def test_crowd_auth_failure_via_login_endpoint(mock_crowd_class, client, app):
    """Failed Crowd auth via /auth/login returns 401."""
    mock_server = MagicMock()
    mock_server.auth_user.return_value = None
    mock_crowd_class.return_value = mock_server

    app.config.update({
        'AUTHENTICATOR': 'nginxauthdaemon.crowdauth.CrowdAuthenticator',
        'CROWD_URL': 'http://crowd.example.com/crowd/',
        'CROWD_APP_NAME': 'testapp',
        'CROWD_APP_PASSWORD': 'testpass',
    })

    resp = client.post('/auth/login', data={
        'user': 'crowduser',
        'pass': 'badpass',
        'target': '/dashboard'
    })
    assert resp.status_code == 401
    assert client.get_cookie('auth_session') is None

    # Reset
    app.config['AUTHENTICATOR'] = 'nginxauthdaemon.auth.DummyAuthenticator'
