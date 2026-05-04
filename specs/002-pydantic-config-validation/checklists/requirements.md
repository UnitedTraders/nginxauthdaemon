# Requirements Checklist — 002 Pydantic Config Validation

| Field | Value |
|-------|-------|
| Feature | Strict configuration validation with Pydantic |
| Created | 2026-05-04 |
| Branch | `002-pydantic-config-validation` |

## Configuration Model

- [x] CHK001 Pydantic `AppConfig` model created with all config fields typed
- [x] CHK002 `DES_KEY` validated as exactly 8 bytes
- [x] CHK003 `SESSION_SALT` validated as non-default placeholder
- [x] CHK004 `JWT_PRIVATE_KEY` validated as valid RSA PEM key
- [x] CHK005 `AUTH_URL_PREFIX` has default value `/auth`
- [x] CHK006 `AUTHENTICATOR` field validates against known authenticator classes
- [x] CHK007 Pydantic v2 and pydantic-settings v2 used

## Authenticator Validation

- [x] CHK008 `CrowdAuthenticator` is the default authenticator
- [x] CHK009 `DummyAuthenticator` blocked unless `TESTING=True` or `ALLOW_DUMMY_AUTH=True`
- [x] CHK010 Crowd config fields (`CROWD_URL`, `CROWD_APP_NAME`, `CROWD_APP_PASSWORD`) required when Crowd authenticator selected
- [x] CHK011 `CROWD_URL` validated as well-formed URL
- [x] CHK012 Clear error message when DummyAuthenticator used in production

## Config Loading

- [x] CHK013 TOML config files load correctly via pydantic-settings
- [x] CHK014 `DAEMON_SETTINGS` env var loading preserved
- [x] CHK015 Environment variable overrides work
- [x] CHK016 Flask `app.config` populated from validated Pydantic model

## Backward Compatibility

- [x] CHK017 New `example.toml` replaces `example.cfg`
- [x] CHK018 Session cookie format unchanged (DES + salt)
- [x] CHK019 JWT token format unchanged (RS256)
- [x] CHK020 HTTP API routes unchanged

## Testing

- [x] CHK021 All 24 existing tests pass
- [x] CHK022 Test config (`tests/test_config.toml`) works with validation
- [x] CHK023 New tests for config validation (missing fields, invalid values)
- [x] CHK024 New tests for DummyAuthenticator production blocking

## Dependencies

- [x] CHK025 `pydantic>=2.0` added to `requirements.txt`
- [x] CHK026 `pydantic-settings>=2.0` added to `requirements.txt`
- [x] CHK027 Docker build succeeds with new dependencies

## Notes

- All 27 items completed
- 55 total tests (24 original + 31 new validation tests)
- Docker build verified
