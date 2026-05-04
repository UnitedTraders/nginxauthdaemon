# Research: Pydantic Config Validation

## Decision: Pydantic Settings with TOML

**Decision**: Use `pydantic-settings>=2.6.0` with built-in `TomlConfigSettingsSource` for TOML config loading.

**Rationale**: pydantic-settings v2.6+ includes native TOML file support via `TomlConfigSettingsSource`. On Python 3.11+, it uses stdlib `tomllib` — no extra dependency needed. This provides type validation, environment variable overrides, and TOML loading in a single framework.

**Alternatives considered**:
- Custom TOML settings source with `tomllib` directly — unnecessary since built-in support exists
- Keep Python module config format with Flask's `from_envvar` — less safe, no type validation
- YAML config — requires PyYAML dependency, TOML is simpler for flat key-value configs

## Decision: App Factory Pattern

**Decision**: Use Flask's `create_app(config_path=None)` factory pattern.

**Rationale**: The current module-level app creation (`app = Flask(__name__)` at import time) forces config to be set via env vars before import. The factory pattern:
- Allows explicit config path passing (cleaner tests)
- Validates config via Pydantic before route registration
- Is the standard Flask pattern for testable apps
- Still exports `app` from `__init__.py` for gunicorn compatibility

**Alternatives considered**:
- Module-level creation (current) — forces env var hacks in tests, validation timing issues
- Lazy validation on first request — too late, config errors should fail at startup

## Decision: Authenticator String Enum

**Decision**: Replace dotted class path string with simple enum: `"crowd"` or `"dummy"`.

**Rationale**: Eliminates arbitrary class loading from config files. The mapping is:
- `"crowd"` → `nginxauthdaemon.crowdauth.CrowdAuthenticator`
- `"dummy"` → `nginxauthdaemon.auth.DummyAuthenticator` (only when `testing = true`)

**Alternatives considered**:
- Keep dotted path with allowlist — still exposes internal module structure in config
- Remove from config entirely — too inflexible, tests need DummyAuthenticator

## Key Findings: pydantic-settings TOML Support

- `pydantic-settings>=2.6.0` provides `TomlConfigSettingsSource` built-in
- Configure via `model_config = SettingsConfigDict(toml_file='config.toml')`
- Override `settings_customise_sources()` to set priority: env vars > TOML file > defaults
- Python 3.13 uses stdlib `tomllib` — no extra package needed
- Latest compatible versions: `pydantic==2.11.3`, `pydantic-settings==2.9.1`
- TOML file path can be overridden at runtime via constructor or env var

## Minimal Example

```python
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(toml_file='config.toml')

    realm_name: str = "Realm"
    authenticator: str = "crowd"

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (
            kwargs.get('env_settings', None),       # env vars highest priority
            TomlConfigSettingsSource(settings_cls),  # TOML file
            kwargs.get('init_settings', None),       # init kwargs lowest
        )
```
