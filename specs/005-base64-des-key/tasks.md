# Tasks: Base64 DES Key Format

**Input**: Design documents from `/specs/005-base64-des-key/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

_No setup tasks needed — this feature modifies existing files only._

---

## Phase 2: Foundational

These tasks change the core config model and DES key usage. All user stories depend on these.

- [x] T001 Update `des_key` default placeholder in `nginxauthdaemon/config.py` — replace raw unicode escape default `'\xc8\x9a\x17\x8f\x17\xd7\x93:'` with base64 constant `_DEFAULT_PLACEHOLDER_DES_KEY = "yJoXjxfXkzo="` and set `des_key: str = _DEFAULT_PLACEHOLDER_DES_KEY`
- [x] T002 Rewrite `validate_des_key` field validator in `nginxauthdaemon/config.py` — (1) reject default placeholder value like `session_salt` does, (2) attempt `base64.b64decode(v)` and raise ValueError with message `des_key is not valid base64` on failure, (3) check `len(decoded) == 8` and raise ValueError with message `des_key must decode to exactly 8 bytes, got {n}` if wrong, (4) return the original base64 string
- [x] T003 Add `DES_KEY_BYTES` to `to_flask_config()` in `nginxauthdaemon/config.py` — add `result['DES_KEY_BYTES'] = base64.b64decode(self.des_key)` so Flask app receives decoded bytes directly
- [x] T004 Update `create_session_cookie()` in `nginxauthdaemon/nginxauthdaemon.py` — replace `DES.new(bytes(current_app.config['DES_KEY'], encoding="raw_unicode_escape"), DES.MODE_ECB)` with `DES.new(current_app.config['DES_KEY_BYTES'], DES.MODE_ECB)`
- [x] T005 Update `decode_session_cookie()` in `nginxauthdaemon/nginxauthdaemon.py` — same replacement as T004 for the decode path

---

## Phase 3: US1 — Base64 Key Configuration (P1)

**Story goal**: Operators can specify the DES key as a base64 string and use standard tools to generate it.

**Independent test criteria**: App starts with a valid base64 `des_key` in config; session cookie encryption/decryption works correctly.

- [x] T006 [US1] Update `tests/test_config.toml` — change `des_key` value from `"\u00c8\u009a\u0017\u008f\u0017\u00d7\u0093:"` to `"yJoXjxfXkzo="`
- [x] T007 [US1] Update `_make_config()` helper in `tests/test_config_validation.py` — change `des_key` default from `'\xc8\x9a\x17\x8f\x17\xd7\x93:'` to `'yJoXjxfXkzo='`
- [x] T008 [US1] Update existing DES key length validation tests in `tests/test_config_validation.py` — update `test_des_key_must_be_8_bytes_rejects_short` and `test_des_key_must_be_8_bytes_rejects_long` to use base64 values that decode to wrong lengths (e.g., `"dGVzdA=="` for 4 bytes, `"dGVzdHRlc3R0ZXN0dA=="` for 10+ bytes) and update expected error messages
- [x] T009 [US1] Update `test_des_key_valid_8_bytes_accepted` in `tests/test_config_validation.py` — use a valid base64 key like `"yJoXjxfXkzo="` and verify config loads successfully
- [x] T010 [US1] Update inline TOML strings in `test_load_config_from_toml_file` and `test_env_vars_override_toml` in `tests/test_config_validation.py` — change `des_key` lines from unicode escape format to base64 format
- [x] T011 [US1] Update `test_cookie_with_wrong_des_key_is_rejected` in `tests/test_security.py` — change the wrong key value to a different valid base64 8-byte key (e.g., `"AAAAAAAAAAA="`) and update `DES.new()` call to use `base64.b64decode()` instead of `raw_unicode_escape` encoding
- [x] T012 [US1] Update `test_jwt_access_token_contains_expected_claims` in `tests/test_security.py` — update the DES key construction line (line ~60) to use `base64.b64decode(app.config['DES_KEY'])` instead of `bytes(app.config['DES_KEY'], encoding="raw_unicode_escape")`
- [x] T013 [US1] Run full test suite — `DAEMON_SETTINGS=tests/test_config.toml .venv/bin/python -m pytest tests/ -v` and verify all tests pass

---

## Phase 4: US2 — Clear Error Messages (P1)

**Story goal**: Invalid base64 or wrong decoded length produce clear, actionable error messages.

**Independent test criteria**: Validation errors name the exact problem and state the requirement.

- [x] T014 [US2] Add test `test_des_key_invalid_base64_rejected` in `tests/test_config_validation.py` — verify that `des_key="not-valid-base64!!!"` raises ValidationError matching `not valid base64`
- [x] T015 [US2] Add test `test_des_key_default_placeholder_rejected` in `tests/test_config_validation.py` — create config with default placeholder des_key in non-testing mode and verify it raises ValidationError matching `must be changed from the default placeholder`
- [x] T016 [US2] Run test suite to confirm all error message tests pass

---

## Phase 5: US3 — Updated Example Configuration (P2)

**Story goal**: Example config shows the new base64 format so new deployments follow the correct pattern.

**Independent test criteria**: `example.toml` contains base64 `des_key` with generation instructions.

- [x] T017 [P] [US3] Update `example.toml` — change `des_key` line to `des_key = "yJoXjxfXkzo="` and add comment above: `# DES encryption key (base64-encoded, must decode to exactly 8 bytes)` and `# Generate with: openssl rand -base64 8`
- [x] T018 [P] [US3] Update `CLAUDE.md` Configuration table — change `des_key` description from `8-byte DES key` to `Base64-encoded 8-byte DES key (generate with: openssl rand -base64 8)`

---

## Phase 6: Polish & Cross-Cutting

- [x] T019 Run full test suite one final time — `DAEMON_SETTINGS=tests/test_config.toml .venv/bin/python -m pytest tests/ -v` and verify all 60+ tests pass with zero failures

---

## Dependencies

```
Phase 2 (Foundational: T001-T005)
  ↓
Phase 3 (US1: T006-T013) — depends on Phase 2
  ↓
Phase 4 (US2: T014-T016) — depends on Phase 2 (can run parallel with Phase 3)

Phase 5 (US3: T017-T018) — independent of Phase 3/4, only depends on Phase 2 design decisions

Phase 6 (Polish: T019) — depends on all above
```

## Implementation Strategy

### MVP Scope

**MVP = Phase 2 + Phase 3 (US1)**: Core config change + test updates. This delivers the primary value: operators can use base64 keys.

### Incremental Delivery

1. Complete Phase 2 (Foundational) → app uses base64 keys internally
2. Complete Phase 3 (US1) → all tests updated and passing
3. Complete Phase 4 (US2) → error message tests added
4. Complete Phase 5 (US3) → docs and example updated
5. Complete Phase 6 (Polish) → final validation

### Parallel Opportunities

- T017 and T018 (Phase 5) can run in parallel — different files
- Phase 4 (US2) can start in parallel with Phase 3 (US1) after Phase 2 completes — they touch the same test file but different test functions

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All tasks modify existing files — no new application files created
- The base64 equivalent of the current test key `'\xc8\x9a\x17\x8f\x17\xd7\x93:'` is `"yJoXjxfXkzo="`
- Commit after each phase completion
