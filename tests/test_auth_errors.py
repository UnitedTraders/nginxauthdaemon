"""Tests for authentication backend error handling.

Verifies that auth backend failures (network errors, timeouts, etc.)
return proper error responses instead of unhandled 500 errors.
"""
from unittest.mock import patch


def test_form_login_backend_exception_returns_503(client):
    """Form login with backend exception returns 503 with error message."""
    with patch('nginxauthdaemon.nginxauthdaemon.get_authenticator') as mock_auth:
        mock_auth.return_value.authenticate.side_effect = Exception("Connection refused")
        resp = client.post('/auth/login', data={
            'user': 'testuser',
            'pass': 'testpass',
            'target': '/'
        })
    assert resp.status_code == 503
    assert b'temporarily unavailable' in resp.data


def test_form_login_connection_error_returns_503(client):
    """Form login with ConnectionError returns 503 and renders login page."""
    with patch('nginxauthdaemon.nginxauthdaemon.get_authenticator') as mock_auth:
        mock_auth.return_value.authenticate.side_effect = ConnectionError("Connection refused")
        resp = client.post('/auth/login', data={
            'user': 'testuser',
            'pass': 'testpass',
            'target': '/'
        })
    assert resp.status_code == 503
    assert b'<form' in resp.data
    assert b'temporarily unavailable' in resp.data


def test_validate_backend_exception_returns_503(client):
    """Basic Auth validate with backend exception returns 503, not 500."""
    import base64
    credentials = base64.b64encode(b'testuser:testpass').decode('ascii')
    with patch('nginxauthdaemon.nginxauthdaemon.get_authenticator') as mock_auth:
        mock_auth.return_value.authenticate.side_effect = Exception("Timeout")
        resp = client.get('/auth/validate', headers={
            'Authorization': f'Basic {credentials}'
        })
    assert resp.status_code == 503
    assert b'service unavailable' in resp.data.lower()


def test_error_response_does_not_expose_internal_details(client):
    """Error response body must not contain the exception message."""
    with patch('nginxauthdaemon.nginxauthdaemon.get_authenticator') as mock_auth:
        mock_auth.return_value.authenticate.side_effect = ConnectionError(
            "Failed to connect to crowd.internal.company.com:8095"
        )
        resp = client.post('/auth/login', data={
            'user': 'testuser',
            'pass': 'testpass',
            'target': '/'
        })
    assert resp.status_code == 503
    assert b'crowd.internal.company.com' not in resp.data
    assert b'8095' not in resp.data
    assert b'Failed to connect' not in resp.data


def test_wrong_credentials_still_returns_401(client):
    """Wrong credentials path is unchanged — returns 401 with credential error."""
    resp = client.post('/auth/login', data={
        'user': 'testuser',
        'pass': 'wrongpass',
        'target': '/'
    })
    assert resp.status_code == 401
    assert b'Please check user name and password' in resp.data
