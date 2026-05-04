import os
import base64

# Set DAEMON_SETTINGS before importing the app — required because the app
# reads AUTH_URL_PREFIX at module level during import.
os.environ['DAEMON_SETTINGS'] = os.path.join(
    os.path.dirname(__file__), 'test_config.cfg'
)

import pytest
import jwt
from cryptography.hazmat.primitives import serialization
from nginxauthdaemon import app as flask_app


# RSA public key derived from DefaultConfig private key for JWT verification
def _get_public_key():
    private_key_pem = flask_app.config['JWT_PRIVATE_KEY'].strip().encode()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


@pytest.fixture
def app():
    """Create Flask application configured for testing."""
    flask_app.config.update({
        'TESTING': True,
        'AUTHENTICATOR': 'nginxauthdaemon.auth.DummyAuthenticator',
    })
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client with cookie jar persistence."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def public_key():
    """RSA public key for JWT verification."""
    return _get_public_key()


def make_basic_auth_header(username, password):
    """Create a Basic Auth header value."""
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {credentials}"
