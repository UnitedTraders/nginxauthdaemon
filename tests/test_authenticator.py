"""Integration tests for pluggable authenticator contract."""
import pytest
from nginxauthdaemon.auth import DummyAuthenticator, Authenticator


def test_dummy_authenticator_accepts_matching_credentials():
    """DummyAuthenticator returns True when username == password."""
    auth = DummyAuthenticator({})
    assert auth.authenticate('testuser', 'testuser') is True


def test_dummy_authenticator_rejects_non_matching_credentials():
    """DummyAuthenticator returns False when username != password."""
    auth = DummyAuthenticator({})
    assert auth.authenticate('testuser', 'wrongpass') is False


def test_custom_authenticator_loaded_via_config(client, app):
    """A custom authenticator class can be plugged in via configuration."""
    # Configure a custom authenticator that always succeeds
    app.config['AUTHENTICATOR'] = 'tests.test_authenticator.AlwaysTrueAuthenticator'

    resp = client.post('/auth/login', data={
        'user': 'anyone',
        'pass': 'anything',
        'target': '/'
    })
    assert resp.status_code == 302  # Redirect = successful login

    # Reset to default
    app.config['AUTHENTICATOR'] = 'nginxauthdaemon.auth.DummyAuthenticator'


def test_invalid_authenticator_path_raises_error(client, app):
    """An invalid authenticator class path causes an ImportError."""
    app.config['AUTHENTICATOR'] = 'nonexistent.module.FakeAuthenticator'

    with pytest.raises((ImportError, ModuleNotFoundError)):
        client.post('/auth/login', data={
            'user': 'test',
            'pass': 'test',
            'target': '/'
        })

    # Reset to default
    app.config['AUTHENTICATOR'] = 'nginxauthdaemon.auth.DummyAuthenticator'


# --- Test helper: custom authenticator for testing pluggability ---

class AlwaysTrueAuthenticator(Authenticator):
    """Test authenticator that always accepts credentials."""
    def authenticate(self, username, password):
        return True
