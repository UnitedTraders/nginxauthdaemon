# Contract: TOML Configuration File Format

## Overview

The daemon configuration file uses TOML format, loaded by `pydantic-settings` via `TomlConfigSettingsSource`.

## File Location

Specified via the `DAEMON_SETTINGS` environment variable:
```bash
DAEMON_SETTINGS=/path/to/config.toml
```

## Schema

```toml
# Required fields — daemon will not start without these
session_salt = "your-long-random-salt-string-here"
des_key = "\xc8\x9a\x17\x8f\x17\xd7\x93:"
jwt_private_key = """
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
"""

# Authenticator selection: "crowd" (default) or "dummy" (test only)
authenticator = "crowd"

# Crowd settings — required when authenticator = "crowd"
crowd_url = "https://crowd.example.com/crowd/"
crowd_app_name = "myapp"
crowd_app_password = "secret"

# Optional fields with defaults
realm_name = "Realm"
session_cookie = "auth_session"
access_token_cookie = "auth_access_token"
target_header = "X-Target"
auth_url_prefix = "/auth"

# Test mode — allows DummyAuthenticator
testing = false
allow_dummy_auth = false
```

## Environment Variable Overrides

All fields can be overridden via environment variables (uppercase, no prefix):

```bash
SESSION_SALT=my-salt DAEMON_SETTINGS=config.toml gunicorn nginxauthdaemon:app
```

Environment variables take precedence over TOML file values.

## Validation Errors

On invalid config, the daemon exits with code 1 and prints a structured error:

```
Configuration error:
  - session_salt: field required
  - des_key: must be exactly 8 bytes
  - authenticator: 'dummy' not allowed in production (set testing=true)
```

## Migration from .cfg

Old Python module format:
```python
REALM_NAME = "Example"
AUTHENTICATOR = 'nginxauthdaemon.crowdauth.CrowdAuthenticator'
CROWD_URL = 'https://crowd.example.com/crowd/'
```

New TOML format:
```toml
realm_name = "Example"
authenticator = "crowd"
crowd_url = "https://crowd.example.com/crowd/"
```

Key changes:
- Field names are lowercase (TOML convention)
- `AUTHENTICATOR` is now a simple string enum, not a dotted class path
- Boolean values use TOML `true`/`false`, not Python `True`/`False`
- Multi-line strings use triple quotes `"""`
