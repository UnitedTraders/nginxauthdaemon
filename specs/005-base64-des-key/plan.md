# Implementation Plan: Base64 DES Key Format

## Technical Context

| Aspect | Detail |
|--------|--------|
| Language / Runtime | Python 3.13 |
| Framework | Flask 3.1.3 |
| Config library | pydantic 2.13.3, pydantic-settings 2.14.0 |
| Crypto library | pycryptodome 3.23.0 (DES-ECB) |
| Config format | TOML via `DAEMON_SETTINGS` env var |
| Test framework | pytest |

**Key files affected**:
- `nginxauthdaemon/config.py` — `AppConfig.des_key` field, validator, default placeholder
- `nginxauthdaemon/nginxauthdaemon.py` — `create_session_cookie()`, `decode_session_cookie()` (DES key usage)
- `example.toml` — config example
- `tests/test_config.toml` — test fixture config
- `tests/test_config_validation.py` — `_make_config()` helper, DES key validation tests
- `tests/test_security.py` — `test_cookie_with_wrong_des_key_is_rejected`
- `CLAUDE.md` — documentation

**No unknowns / NEEDS CLARIFICATION**: All design decisions are resolved.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security-First | PASS | Secrets stay out of source control; uses pycryptodome; adds placeholder rejection guard |
| II. Explicit Configuration | PASS | Default placeholder rejected at startup (FR-007); config key documented |
| III. Pluggable Architecture | N/A | No authenticator changes |
| IV. Defensive Coding | PASS | Invalid base64 and wrong length produce clear validation errors at startup |
| V. Minimal Dependencies | PASS | No new dependencies; base64 is stdlib |
| Dev Workflow: example+docs | PASS | example.toml and CLAUDE.md updated |

No violations. No entries needed in Complexity Tracking.

## Implementation Design

### Change 1: Config model (`config.py`)

**Default placeholder**: Change from raw unicode escape to base64 string:
```
# Before
des_key: str = '\xc8\x9a\x17\x8f\x17\xd7\x93:'

# After
_DEFAULT_PLACEHOLDER_DES_KEY = "yJoXjxfXkzo="
des_key: str = _DEFAULT_PLACEHOLDER_DES_KEY
```

**Validator `validate_des_key`**: Replace the current raw_unicode_escape logic:
1. Reject default placeholder (like `session_salt` does)
2. Attempt `base64.b64decode(v)` — raise ValueError on invalid base64
3. Check decoded length == 8 — raise ValueError with actual length if wrong
4. Return the original base64 string (keep storage as base64)

**New property or method**: Add a `des_key_bytes` property (or resolve in `to_flask_config`) so the Flask app receives the decoded bytes directly. This avoids repeating base64 decode at every request.

### Change 2: DES key usage (`nginxauthdaemon.py`)

**`create_session_cookie()`** and **`decode_session_cookie()`**: Replace:
```python
des = DES.new(bytes(current_app.config['DES_KEY'], encoding="raw_unicode_escape"), DES.MODE_ECB)
```
with:
```python
des = DES.new(current_app.config['DES_KEY_BYTES'], DES.MODE_ECB)
```

The `DES_KEY_BYTES` value is set in `to_flask_config()` as `base64.b64decode(self.des_key)`.

### Change 3: Config file updates

**`example.toml`**: Change `des_key` line to:
```toml
# DES encryption key (base64-encoded, must decode to exactly 8 bytes)
# Generate with: openssl rand -base64 8
des_key = "yJoXjxfXkzo="
```

**`tests/test_config.toml`**: Same format change.

### Change 4: Test updates

- `tests/test_config_validation.py`:
  - `_make_config()`: use `des_key='yJoXjxfXkzo='`
  - Update existing DES key validation tests for new error messages (base64 decode error, wrong length)
  - Add test: default placeholder rejected (non-testing mode)
  - Update inline TOML strings in `test_load_config_from_toml_file` etc.

- `tests/test_security.py`:
  - `test_cookie_with_wrong_des_key_is_rejected`: update to use a different base64 key
  - `test_jwt_access_token_contains_expected_claims`: update DES key construction line

### Change 5: Documentation

- `CLAUDE.md`: Update `des_key` description in Configuration table to say "Base64-encoded 8-byte DES key"

## Project Structure

No new files or directories. All changes are to existing files:

```
nginxauthdaemon/
├── config.py              # Modified: des_key default, validator, to_flask_config
├── nginxauthdaemon.py     # Modified: DES.new() calls use DES_KEY_BYTES
tests/
├── test_config.toml       # Modified: des_key value
├── test_config_validation.py  # Modified: _make_config, validation tests
├── test_security.py       # Modified: wrong-key test
example.toml               # Modified: des_key value + comment
CLAUDE.md                  # Modified: des_key description
```
