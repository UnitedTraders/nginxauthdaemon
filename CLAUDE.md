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
DAEMON_SETTINGS=/path/to/config.cfg python -m nginxauthdaemon.nginxauthdaemon
# Or with gunicorn:
DAEMON_SETTINGS=/path/to/config.cfg gunicorn -b 0.0.0.0:5000 -k eventlet nginxauthdaemon:app

# Docker
docker build -t nginxauthdaemon .
docker run -p 5000:5000 -v $(pwd)/example.cfg:/example.cfg -e DAEMON_SETTINGS=/example.cfg -e WEB_CONCURRENCY=4 nginxauthdaemon

# Install as package (editable)
pip install -e .
```

There are no tests in this project currently (coverage is listed as a dev dependency but no test files exist).

## Architecture

```
nginxauthdaemon/
├── __init__.py          # Exports `app` (Flask WSGI application)
├── nginxauthdaemon.py   # Main Flask app: routes, session cookie crypto, JWT creation
├── config.py            # DefaultConfig class with all default settings
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

### Key Design Points

- **Pluggable authenticators**: Set `AUTHENTICATOR` config to a dotted class path (e.g., `nginxauthdaemon.crowdauth.CrowdAuthenticator`). Must implement `authenticate(username, password) -> bool`.
- **Session cookies**: DES-ECB encrypted with a salt suffix for verification. 7-day expiry.
- **JWT access tokens**: RS256-signed, contain `user_id`, issued alongside session cookies.
- **Configuration**: Python module loaded via `DAEMON_SETTINGS` env var pointing to a .cfg/.py file. Overrides values in `config.py:DefaultConfig`.

## Configuration

Key settings (override in your config file):

| Setting | Purpose |
|---------|---------|
| `AUTHENTICATOR` | Dotted path to authenticator class |
| `SESSION_SALT` | Salt appended before DES encryption (must override for security) |
| `DES_KEY` | 8-byte DES key (must override for security) |
| `JWT_PRIVATE_KEY` | RSA private key for JWT signing |
| `AUTH_URL_PREFIX` | URL prefix for auth routes (default: `/auth`) |
| `REALM_NAME` | Displayed on login page |
| `SESSION_COOKIE` | Cookie name for session |
| `ACCESS_TOKEN_COOKIE` | Cookie name for JWT |
| `TARGET_HEADER` | Header nginx uses to pass the original URL (default: `X-Target`) |

## Dependencies

- **Flask 2.3.2** - web framework
- **pycryptodome 3.19.1** - DES encryption for session cookies
- **PyJWT 2.4.0** - JWT token generation
- **Crowd 2.0.1** - Atlassian Crowd client library
- **gunicorn + eventlet** - production WSGI server

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
