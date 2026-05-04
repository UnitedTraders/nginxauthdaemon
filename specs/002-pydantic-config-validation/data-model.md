# Data Model: AppConfig

## Entity: AppConfig (Pydantic BaseSettings)

The central configuration model that replaces `DefaultConfig` class.

### Fields

| Field | Type | Default | Validation | Required |
|-------|------|---------|------------|----------|
| `realm_name` | `str` | `"Realm"` | Non-empty | No |
| `session_cookie` | `str` | `"auth_session"` | Non-empty | No |
| `target_header` | `str` | `"X-Target"` | Non-empty | No |
| `session_salt` | `str` | — | Must not equal default placeholder; min 16 chars | Yes |
| `des_key` | `str` | — | Must be exactly 8 bytes when encoded | Yes |
| `authenticator` | `AuthenticatorType` | `"crowd"` | Enum: `"crowd"`, `"dummy"` | No |
| `jwt_private_key` | `str` | — | Must be valid RSA PEM private key | Yes |
| `access_token_cookie` | `str` | `"auth_access_token"` | Non-empty | No |
| `auth_url_prefix` | `str` | `"/auth"` | Must start with `/` | No |
| `testing` | `bool` | `False` | — | No |
| `allow_dummy_auth` | `bool` | `False` | — | No |

### Conditional Fields (when `authenticator == "crowd"`)

| Field | Type | Default | Validation | Required |
|-------|------|---------|------------|----------|
| `crowd_url` | `str` | — | Valid URL format | Yes (when crowd) |
| `crowd_app_name` | `str` | — | Non-empty | Yes (when crowd) |
| `crowd_app_password` | `str` | — | Non-empty | Yes (when crowd) |

### Enum: AuthenticatorType

```
"crowd"  → nginxauthdaemon.crowdauth.CrowdAuthenticator
"dummy"  → nginxauthdaemon.auth.DummyAuthenticator
```

### Validation Rules

1. **DES_KEY length**: `len(des_key.encode('raw_unicode_escape')) == 8`
2. **SESSION_SALT non-default**: Salt must not equal the hardcoded default `"3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="`
3. **JWT_PRIVATE_KEY format**: Must contain `BEGIN RSA PRIVATE KEY` or `BEGIN PRIVATE KEY`
4. **DummyAuthenticator guard**: If `authenticator == "dummy"` and `testing == False` and `allow_dummy_auth == False`, raise `ValidationError`
5. **Crowd fields required**: If `authenticator == "crowd"`, then `crowd_url`, `crowd_app_name`, `crowd_app_password` must all be non-empty
6. **AUTH_URL_PREFIX format**: Must start with `/`, no trailing slash

### State Transitions

N/A — config is immutable after validation. The `AppConfig` model is created once during `create_app()` and never modified.

### Relationships

```
AppConfig --creates--> Flask app (app.config populated from model)
AppConfig --selects--> Authenticator class (via authenticator enum)
AppConfig --validates--> Crowd settings (conditional on authenticator choice)
```
