import os
import base64

import pytest
import jwt
from cryptography.hazmat.primitives import serialization

from nginxauthdaemon.nginxauthdaemon import create_app


_test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.toml')


def _get_public_key(app):
    """Derive RSA public key from the app's configured private key."""
    private_key_pem = app.config['JWT_PRIVATE_KEY'].strip().encode()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


@pytest.fixture
def app():
    """Create Flask application configured for testing."""
    flask_app = create_app(_test_config_path)
    flask_app.config.update({
        'TESTING': True,
    })
    yield flask_app


@pytest.fixture
def client(app):
    """Flask test client with cookie jar persistence."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def public_key(app):
    """RSA public key for JWT verification."""
    return _get_public_key(app)


def make_basic_auth_header(username, password):
    """Create a Basic Auth header value."""
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {credentials}"
