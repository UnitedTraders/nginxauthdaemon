# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

nginxauthdaemon is a Python Flask authentication daemon designed as a backend for nginx's `auth_request` module. It validates sessions via encrypted cookies (DES + salt) and issues JWT access tokens. It integrates with nginx (or HAProxy) to protect upstream applications.

## Development Commands

```bash
# Setup
virtualenv env && . ./env/bin/activate
pip install -r requirements.txt
pip install -r requirements-run.txt

# Run locally (development)
DAEMON_SETTINGS=/path/to/config.toml python -m nginxauthdaemon.nginxauthdaemon
# Or with gunicorn:
DAEMON_SETTINGS=/path/to/config.toml gunicorn -b 0.0.0.0:5000 -k gthread --threads 4 nginxauthdaemon.wsgi:app

# Docker
docker build -t nginxauthdaemon .
docker run -p 5000:5000 -v $(pwd)/example.toml:/app/config.toml -e DAEMON_SETTINGS=/app/config.toml -e WEB_CONCURRENCY=4 nginxauthdaemon

# Run tests
.venv/bin/python -m pytest tests/ -v
```

## Testing

Integration tests live in `tests/`. Run with:

```bash
pip install -r requirements-test.txt -r requirements.txt cryptography
DAEMON_SETTINGS=tests/test_config.toml pytest tests/ -v
```

## Architecture

```
nginxauthdaemon/
├── __init__.py          # Exports `create_app` factory function
├── wsgi.py              # WSGI entry point: creates app for gunicorn
├── nginxauthdaemon.py   # Flask app factory: create_app(), routes, session cookie crypto, JWT creation
├── config.py            # Pydantic AppConfig model with validators, TOML loading
├── auth.py              # Base Authenticator class + DummyAuthenticator
├── crowdauth.py         # Atlassian Crowd authenticator implementation
├── templates/login.html # Login form template
└── static/              # Static assets for login page
```

### Request Flow

1. nginx receives a request to a protected location
2. nginx makes a subrequest to `/auth/validate` (this daemon)
3. The daemon checks for a valid session cookie (DES-encrypted, salt-verified) or Basic Auth header
4. If valid → 200; if invalid → 401 (nginx redirects to `/auth/login`)
5. `/auth/login` POST authenticates credentials via the configured Authenticator
6. On success: sets encrypted session cookie + JWT access token cookie, redirects to target URL

### App Factory Pattern

The Flask app is created via `create_app(config_path=None)` factory function in `nginxauthdaemon.py`. Config is loaded from a TOML file (specified by `config_path` parameter or `DAEMON_SETTINGS` env var), validated by Pydantic, and then used to configure the Flask app.

### Key Design Points

- **Pluggable authenticators**: Set `authenticator` config to `"crowd"` (default) or `"dummy"` (test only). Must implement `authenticate(username, password) -> bool`.
- **Configuration**: Pydantic `AppConfig` model loaded from TOML file via `DAEMON_SETTINGS` env var. Validated at startup with clear error messages.
- **Session cookies**: DES-ECB encrypted with a salt suffix for verification. 7-day expiry.
- **JWT access tokens**: RS256-signed, contain `user_id`, issued alongside session cookies.
- **Config file format**: TOML (`.toml`). See `example.toml` for reference.

## Configuration

Configuration uses TOML format. Key settings (override in your `.toml` config file):

| Setting | Purpose |
|---------|---------|
| `authenticator` | Authenticator type: `"crowd"` (default) or `"dummy"` (test only) |
| `session_salt` | Salt appended before DES encryption (must override for security) |
| `des_key` | Base64-encoded 8-byte DES key (generate with: `openssl rand -base64 8`; must override for security) |
| `jwt_private_key` | RSA private key for JWT signing (must override for security) |
| `auth_url_prefix` | URL prefix for auth routes (default: `/auth`) |
| `realm_name` | Displayed on login page |
| `session_cookie` | Cookie name for session |
| `access_token_cookie` | Cookie name for JWT |
| `target_header` | Header nginx uses to pass the original URL (default: `X-Target`) |
| `testing` | Set to `true` to allow DummyAuthenticator |
| `crowd_url` | Crowd server URL (required when `authenticator = "crowd"`) |
| `crowd_app_name` | Crowd application name |
| `crowd_app_password` | Crowd application password |

## Dependencies

- **Flask 3.1.3** - web framework
- **pycryptodome 3.23.0** - DES encryption for session cookies
- **PyJWT 2.12.1** - JWT token generation
- **cryptography 48.0.0** - RSA key support for PyJWT RS256 signing
- **Crowd 3.1.0** - Atlassian Crowd client library
- **pydantic 2.13.3** - configuration validation
- **pydantic-settings 2.14.0** - TOML config file loading
- **gunicorn 25.3.0** - production WSGI server (gthread workers)

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/005-base64-des-key/plan.md
<!-- SPECKIT END -->
