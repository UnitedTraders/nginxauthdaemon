# Pydantic Config Validation

| Field | Value |
|-------|-------|
| Feature | Strict configuration validation with Pydantic |
| Author | AI-assisted |
| Status | Draft |
| Created | 2026-05-04 |
| Branch | `002-pydantic-config-validation` |

## Overview

Replace the current class-reference-based Flask configuration (`DefaultConfig` class + `DAEMON_SETTINGS` env var) with a validated configuration model using Pydantic. Harden the authenticator selection so that `CrowdAuthenticator` is the only production authenticator and `DummyAuthenticator` is restricted to test environments. Add strict validation for all configuration values at startup time.

## User Stories

### US-001: Validated Configuration at Startup (P1)

**As a** deployment engineer,
**I want** the daemon to validate all configuration values at startup and fail with clear error messages if anything is missing or invalid,
**So that** misconfigurations are caught immediately rather than causing runtime failures.

**Acceptance Criteria:**
- The daemon validates all required config values before accepting any requests.
- Validation runs inside an explicit `create_app()` factory function — the app is no longer created at module import time.
- Missing required values produce a clear error message naming the missing field.
- Invalid value types (e.g., non-integer port, malformed RSA key) produce descriptive errors.
- The `DES_KEY` must be exactly 8 bytes.
- The `SESSION_SALT` must not be the default placeholder value in production.
- The `JWT_PRIVATE_KEY` must be a valid RSA private key in PEM format.

### US-002: Remove DummyAuthenticator from Production (P1)

**As a** security engineer,
**I want** the daemon to refuse to start with `DummyAuthenticator` in production mode,
**So that** the trivial username-equals-password authenticator cannot accidentally be deployed.

**Acceptance Criteria:**
- The `AUTHENTICATOR` config setting accepts a simple string enum: `"crowd"` (default) or `"dummy"`. The app maps these internally to the corresponding class. Dotted class paths are no longer accepted.
- `CrowdAuthenticator` is the default (and only) production authenticator.
- `DummyAuthenticator` is only usable when `TESTING = True` or when an explicit `ALLOW_DUMMY_AUTH = True` flag is set.
- Attempting to start with `DummyAuthenticator` in production logs a clear error and exits.

### US-003: Crowd-Specific Config Validation (P1)

**As a** deployment engineer,
**I want** Crowd-specific settings (`CROWD_URL`, `CROWD_APP_NAME`, `CROWD_APP_PASSWORD`) to be required when `CrowdAuthenticator` is selected,
**So that** the daemon fails fast with a clear message instead of crashing on the first auth request.

**Acceptance Criteria:**
- When `CrowdAuthenticator` is the authenticator, `CROWD_URL`, `CROWD_APP_NAME`, and `CROWD_APP_PASSWORD` are all required.
- Missing Crowd settings produce a validation error at startup listing all missing fields.
- `CROWD_URL` is validated as a well-formed URL.

### US-004: Pydantic-Based Config Model (P2)

**As a** developer,
**I want** the configuration to be modeled as a Pydantic `BaseSettings` class,
**So that** I get type coercion, validation, and clear schema documentation in one place.

**Acceptance Criteria:**
- A new `AppConfig` Pydantic model replaces `DefaultConfig`.
- The app uses a `create_app(config_path=None)` factory function. The factory loads and validates config via Pydantic, then constructs the Flask app.
- `__init__.py` calls `create_app()` to provide the default `app` export for gunicorn/WSGI compatibility.
- The model loads values from a TOML config file (pointed to by `DAEMON_SETTINGS` env var) and environment variables via `pydantic-settings`.
- All fields have explicit types and validators.
- The `AUTHENTICATOR` field is a string enum (`"crowd"`, `"dummy"`) — no longer a dotted class path.
- The model is the single source of truth for configuration — Flask's `app.config` is populated from the validated model.
- Python module config file format (`.cfg`) is no longer supported; TOML is the sole file format.

### US-005: TOML Config File Format (P2)

**As a** operator,
**I want** configuration to use TOML format loaded natively by `pydantic-settings`,
**So that** the config format is standardized, human-readable, and validated at load time.

**Acceptance Criteria:**
- Config files migrate from Python module format (`.cfg`) to TOML format (`.toml`).
- The `DAEMON_SETTINGS` environment variable now points to a `.toml` file.
- `pydantic-settings` loads the TOML file natively via a custom settings source.
- Environment variable overrides continue to work (higher priority than file values).
- The `AUTH_URL_PREFIX` setting continues to function.
- Session cookies created by the previous version remain valid (no crypto parameter changes).
- `example.cfg` is replaced by `example.toml` with equivalent settings.
- Old Python module `.cfg` files are no longer supported — migration is a clean break.

### US-006: Test Environment Support (P3)

**As a** developer writing tests,
**I want** to easily configure the daemon for testing with `DummyAuthenticator`,
**So that** integration tests don't require a real Crowd server.

**Acceptance Criteria:**
- Test config files use TOML format and can set `testing = true` to unlock `DummyAuthenticator`.
- The `conftest.py` pattern is simplified: tests call `create_app(config_path="tests/test_config.toml")` directly — no env var manipulation before import is needed.
- A test helper or fixture can create a valid test config programmatically.

## Non-Functional Requirements

- **NFR-001**: Startup time must not increase by more than 100ms due to config validation.
- **NFR-002**: Pydantic v2 must be used (not v1) for performance and modern API.
- **NFR-003**: The `pydantic`, `pydantic-settings`, and `tomli` (for Python <3.11, stdlib `tomllib` for 3.11+) packages are added to `requirements.txt`.
- **NFR-004**: No breaking changes to the external HTTP API (routes, cookie format, JWT format).

## Out of Scope

- Migrating from DES to AES encryption (separate future feature).
- Adding new authenticator backends.
- Changing the JWT signing algorithm or payload structure.
- Web UI for configuration management.

## Open Questions

- Should `AUTH_URL_PREFIX` have a default value in the config model, or remain required in the external config? (Recommendation: add default `/auth` to the model.)
- ~~Should the Pydantic model support loading from YAML/TOML in addition to Python modules?~~ **Resolved**: TOML is the sole config file format; Python module format is dropped.

## Success Criteria

- **SC-001**: The daemon refuses to start with invalid or missing required configuration, displaying clear error messages.
- **SC-002**: All 24 existing tests continue to pass without modification (or with minimal test config changes).
- **SC-003**: `DummyAuthenticator` cannot be activated in production mode.
- **SC-004**: New `example.toml` works as a drop-in replacement for the old `example.cfg`.

## Clarifications

### Session 2026-05-04

- Q: How should the authenticator be specified in config files — dotted class path, string enum, or removed from config? → A: Simple string enum (`"crowd"`, `"dummy"`) mapped internally to classes.
- Q: How should the Pydantic model load configuration from config files? → A: Migrate config files to TOML format and use pydantic-settings native loading. Python module `.cfg` format is dropped.
- Q: When should Pydantic config validation run? → A: In an explicit `create_app()` factory function — validation runs at app construction, not at module import time.

## Assumptions

- Pydantic v2 (`pydantic>=2.0`) and `pydantic-settings>=2.0` are compatible with Python 3.13.
- The `DAEMON_SETTINGS` environment variable is the primary config mechanism — it now points to a TOML file instead of a Python module.
- Config files migrate from Python module format (`.cfg`) to TOML format (`.toml`). This is a breaking change for existing deployments requiring config file conversion.
- The `DummyAuthenticator` class itself is preserved in `auth.py` for test use — only its activation in production is blocked.
- The `Authenticator` base class interface (`authenticate(username, password) -> bool`) is unchanged.
- Python 3.13 includes `tomllib` in stdlib, so no extra TOML parsing dependency is needed.
