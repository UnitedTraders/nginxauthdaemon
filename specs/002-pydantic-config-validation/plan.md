# Implementation Plan: Pydantic Config Validation

| Field | Value |
|-------|-------|
| Feature | Strict configuration validation with Pydantic |
| Branch | `002-pydantic-config-validation` |
| Spec | `specs/002-pydantic-config-validation/spec.md` |
| Created | 2026-05-04 |

## Technical Context

| Aspect | Current State | Target State |
|--------|--------------|--------------|
| Config model | `DefaultConfig` class in `config.py` | Pydantic `AppConfig` in `config.py` |
| Config format | Python module (`.cfg`) via Flask `from_envvar` | TOML (`.toml`) via `pydantic-settings` `TomlConfigSettingsSource` |
| App creation | Module-level in `nginxauthdaemon.py` | `create_app()` factory in `nginxauthdaemon.py` |
| Authenticator selection | Dotted class path string + `importlib` | String enum (`"crowd"` / `"dummy"`) with internal mapping |
| Config validation | None (runtime errors) | Pydantic validators at startup |
| DummyAuthenticator | Available in any environment | Gated behind `testing=true` or `allow_dummy_auth=true` |
| Dependencies | Flask, pycryptodome, PyJWT, Crowd | + pydantic, pydantic-settings |

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.0,<3.0 | Config model with validators |
| pydantic-settings | >=2.6.0,<3.0 | TOML settings source, env var loading |

### Files to Modify

| File | Change |
|------|--------|
| `nginxauthdaemon/config.py` | Replace `DefaultConfig` with Pydantic `AppConfig` model |
| `nginxauthdaemon/nginxauthdaemon.py` | Refactor to `create_app()` factory; remove `importlib` authenticator loading |
| `nginxauthdaemon/__init__.py` | Call `create_app()` to export `app` |
| `nginxauthdaemon/auth.py` | No changes (keep `Authenticator` base + `DummyAuthenticator`) |
| `nginxauthdaemon/crowdauth.py` | No changes |
| `requirements.txt` | Add pydantic, pydantic-settings |
| `example.cfg` → `example.toml` | Convert to TOML format |
| `tests/test_config.cfg` → `tests/test_config.toml` | Convert to TOML format |
| `tests/conftest.py` | Use `create_app()` factory instead of env var hack |
| `tests/test_*.py` | Update for any API changes |
| `Dockerfile` | Update `DAEMON_SETTINGS` reference |
| `README.md` | Update config documentation |
| `CLAUDE.md` | Update config documentation |

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security-First | PASS | DummyAuthenticator blocked in production; secrets validated at startup |
| II. Explicit Configuration | PASS | Pydantic model documents all fields with types; fails fast on missing secrets |
| III. Pluggable Architecture | PASS | Authenticator enum maps to classes; base class interface unchanged |
| IV. Defensive Coding | PASS | Config validation catches errors at startup; clear error messages |
| V. Minimal Dependencies | PASS | Adding 2 deps (pydantic, pydantic-settings) justified by config validation need |

## Architecture

### Config Loading Flow

```
DAEMON_SETTINGS env var → TOML file path
                                ↓
                    pydantic-settings loads TOML
                                ↓
                    env var overrides applied
                                ↓
                    AppConfig model validated
                        ↓ (fail → exit with error)
                        ↓ (pass)
                    create_app(config) builds Flask app
                                ↓
                    app.config populated from model
                                ↓
                    routes registered with config values
```

### Authenticator Resolution

```python
AUTHENTICATOR_MAP = {
    "crowd": "nginxauthdaemon.crowdauth.CrowdAuthenticator",
    "dummy": "nginxauthdaemon.auth.DummyAuthenticator",
}
```

The `get_authenticator()` function uses this map instead of raw `importlib` with user-provided class paths.

### Key Design Decisions

1. **TOML field names are lowercase** — TOML convention. Environment variable overrides are uppercase (pydantic-settings default behavior).

2. **`create_app()` accepts optional `config_path`** — If provided, overrides `DAEMON_SETTINGS` env var. Enables clean test setup: `create_app("tests/test_config.toml")`.

3. **`__init__.py` calls `create_app()`** — Maintains backward compatibility with `gunicorn nginxauthdaemon:app`.

4. **Pydantic model_validator for cross-field validation** — Used for:
   - DummyAuthenticator guard (requires `testing=true`)
   - Crowd fields required when `authenticator="crowd"`

5. **No config file migration tool** — TOML format is simple enough for manual conversion. The contract document provides a migration guide.

## Structure Decision

Existing structure preserved. Changes are within existing files:

```
nginxauthdaemon/
├── __init__.py          # Updated: calls create_app()
├── nginxauthdaemon.py   # Updated: create_app() factory, simplified get_authenticator()
├── config.py            # Updated: Pydantic AppConfig replaces DefaultConfig
├── auth.py              # Unchanged
├── crowdauth.py         # Unchanged
├── templates/login.html # Unchanged
└── static/              # Unchanged
```

## Complexity Tracking

No constitution violations — no entries needed.

## Referenced Artifacts

- `specs/002-pydantic-config-validation/research.md` — Technology research
- `specs/002-pydantic-config-validation/data-model.md` — AppConfig field definitions
- `specs/002-pydantic-config-validation/contracts/config-format.md` — TOML config file contract
