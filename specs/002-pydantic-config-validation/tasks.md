# Tasks: Pydantic Config Validation

**Input**: Design documents from `specs/002-pydantic-config-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included — the existing test suite must continue passing and new validation tests are needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

- [x] T001 Add `pydantic>=2.0,<3.0` and `pydantic-settings>=2.6.0,<3.0` to `requirements.txt`
- [x] T002 Install updated dependencies in virtual environment and verify import works

---

## Phase 2: Foundational — Pydantic AppConfig Model

> These tasks create the core config model that all user stories depend on.

- [x] T003 Create `AppConfig` Pydantic BaseSettings model in `nginxauthdaemon/config.py` replacing `DefaultConfig` — define all typed fields with defaults per `data-model.md` (realm_name, session_cookie, target_header, session_salt, des_key, jwt_private_key, access_token_cookie, auth_url_prefix, testing, allow_dummy_auth, authenticator, crowd_url, crowd_app_name, crowd_app_password)
- [x] T004 Add `AuthenticatorType` string enum to `nginxauthdaemon/config.py` with values `"crowd"` and `"dummy"`, set as type for `authenticator` field
- [x] T005 Configure `TomlConfigSettingsSource` in `AppConfig` via `settings_customise_sources()` in `nginxauthdaemon/config.py` — priority: env vars > TOML file > defaults
- [x] T006 Add `AUTHENTICATOR_MAP` dict to `nginxauthdaemon/config.py` mapping enum values to dotted class paths (`"crowd"` → `nginxauthdaemon.crowdauth.CrowdAuthenticator`, `"dummy"` → `nginxauthdaemon.auth.DummyAuthenticator`)
- [x] T007 Refactor `nginxauthdaemon/nginxauthdaemon.py` — extract `create_app(config_path=None)` factory function that: loads `AppConfig` from TOML file (from `config_path` param or `DAEMON_SETTINGS` env var), populates `app.config` from validated model, registers routes, stores config model on app
- [x] T008 Simplify `get_authenticator()` in `nginxauthdaemon/nginxauthdaemon.py` — use `AUTHENTICATOR_MAP` lookup instead of raw `importlib` with user-provided class path
- [x] T009 Update `nginxauthdaemon/__init__.py` to export `create_app`; add `nginxauthdaemon/wsgi.py` as WSGI entry point
- [x] T010 Create `example.toml` replacing `example.cfg` — convert all settings to TOML format per `contracts/config-format.md` with lowercase field names and string enum authenticator
- [x] T011 Create `tests/test_config.toml` replacing `tests/test_config.cfg` — set `authenticator = "dummy"`, `testing = true`, `auth_url_prefix = "/auth"`, and required secret fields with test values
- [x] T012 Update `tests/conftest.py` — use `create_app("tests/test_config.toml")` instead of `os.environ['DAEMON_SETTINGS']` hack before import
- [x] T013 Run existing test suite (`pytest tests/ -v`) and fix any breakage from the refactor

> **Checkpoint**: All 24 existing tests pass with the new config model and factory pattern.

---

## Phase 3: US-001 — Validated Configuration at Startup (P1)

> **Goal**: Daemon fails fast with clear error messages for missing/invalid config.

- [x] T014 [US1] Add `field_validator` for `des_key` in `nginxauthdaemon/config.py` — validate exactly 8 bytes when encoded with `raw_unicode_escape`
- [x] T015 [P] [US1] Add `field_validator` for `session_salt` in `nginxauthdaemon/config.py` — reject the default placeholder value `"3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="` and enforce minimum 16 chars
- [x] T016 [P] [US1] Add `field_validator` for `jwt_private_key` in `nginxauthdaemon/config.py` — validate contains `BEGIN RSA PRIVATE KEY` or `BEGIN PRIVATE KEY`
- [x] T017 [P] [US1] Add `field_validator` for `auth_url_prefix` in `nginxauthdaemon/config.py` — must start with `/`, no trailing slash
- [x] T018 [US1] Add startup error formatting in `create_app()` in `nginxauthdaemon/nginxauthdaemon.py` — catch `ValidationError`, print structured error listing all failing fields, exit with code 1
- [x] T019 [US1] Add tests for config validation errors in `tests/test_config_validation.py` — test missing required fields, invalid DES key length, default salt rejection, malformed JWT key, invalid auth_url_prefix

> **Checkpoint**: `pytest tests/test_config_validation.py -v` passes. Daemon exits cleanly on invalid config.

---

## Phase 4: US-002 — Remove DummyAuthenticator from Production (P1)

> **Goal**: DummyAuthenticator cannot be activated unless `testing=true` or `allow_dummy_auth=true`.

- [x] T020 [US2] Add `model_validator` (mode `after`) in `nginxauthdaemon/config.py` — if `authenticator == "dummy"` and `testing == False` and `allow_dummy_auth == False`, raise `ValueError` with clear message
- [x] T021 [US2] Add tests for DummyAuthenticator blocking in `tests/test_config_validation.py` — test: dummy rejected in production mode, dummy allowed with `testing=true`, dummy allowed with `allow_dummy_auth=true`, crowd always allowed

> **Checkpoint**: `pytest tests/test_config_validation.py -v` passes. DummyAuthenticator blocked in production.

---

## Phase 5: US-003 — Crowd-Specific Config Validation (P1)

> **Goal**: Crowd settings are required when CrowdAuthenticator is selected.

- [x] T022 [US3] Add `model_validator` (mode `after`) in `nginxauthdaemon/config.py` — if `authenticator == "crowd"`, validate `crowd_url`, `crowd_app_name`, `crowd_app_password` are all non-empty strings
- [x] T023 [P] [US3] Add `field_validator` for `crowd_url` in `nginxauthdaemon/config.py` — validate well-formed URL (starts with `http://` or `https://`)
- [x] T024 [US3] Add tests for Crowd config validation in `tests/test_config_validation.py` — test: missing crowd fields when crowd selected, invalid crowd_url, crowd fields ignored when dummy selected

> **Checkpoint**: `pytest tests/test_config_validation.py -v` passes. Crowd config fully validated.

---

## Phase 6: US-004 — Pydantic-Based Config Model (P2)

> **Goal**: AppConfig is the single source of truth; Flask config is populated from it.
> Note: Most of US-004 was implemented in Phase 2 (Foundational). This phase covers remaining acceptance criteria.

- [x] T025 [US4] Verify `app.config` is fully populated from `AppConfig` model in `nginxauthdaemon/nginxauthdaemon.py` — ensure all fields accessible via `app.config['FIELD_NAME']` with uppercase keys for backward compatibility with route handlers
- [x] T026 [US4] Add test in `tests/test_config_validation.py` verifying all AppConfig fields are accessible on `app.config` with correct values

> **Checkpoint**: All config access patterns verified.

---

## Phase 7: US-005 — TOML Config File Format (P2)

> **Goal**: Config files use TOML format loaded by pydantic-settings.
> Note: Most of US-005 was implemented in Phase 2 (Foundational). This phase covers documentation and cleanup.

- [x] T027 [US5] Delete old config files: `example.cfg` and `tests/test_config.cfg`
- [x] T028 [P] [US5] Update `README.md` — replace all references to `.cfg` config format with `.toml`, update Docker launch command to reference `example.toml`, update Configuration section
- [x] T029 [P] [US5] Update `CLAUDE.md` — update Configuration section with new TOML field names, update run commands to reference `.toml` files, update architecture notes about `create_app()` factory
- [x] T030 [P] [US5] Update `Dockerfile` — update `CMD` to use `nginxauthdaemon.wsgi:app`
- [x] T031 [US5] Add test in `tests/test_config_validation.py` verifying env var overrides take precedence over TOML values

> **Checkpoint**: All documentation updated. No `.cfg` references remain.

---

## Phase 8: US-006 — Test Environment Support (P3)

> **Goal**: Tests can easily use DummyAuthenticator.
> Note: Most of US-006 was implemented in Phase 2. This phase ensures test helpers are complete.

- [x] T032 [US6] Verify `tests/conftest.py` `create_app()` call works cleanly with test TOML config — no env var manipulation needed
- [x] T033 [US6] Run full test suite (`pytest tests/ -v`) and confirm all tests pass including new validation tests

> **Checkpoint**: Full test suite green. Test setup is clean.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [x] T034 Run full test suite (`pytest tests/ -v`) — all tests must pass
- [x] T035 Verify Docker build succeeds (`docker build -t nginxauthdaemon .`)
- [x] T036 Update `requirements.txt` with exact pinned versions of pydantic and pydantic-settings after install
- [x] T037 Update checklist at `specs/002-pydantic-config-validation/checklists/requirements.md` — mark completed items

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational)
Phase 2 → Phase 3 (US-001: Validation) [can parallel with Phase 4, 5]
Phase 2 → Phase 4 (US-002: DummyAuth blocking) [can parallel with Phase 3, 5]
Phase 2 → Phase 5 (US-003: Crowd validation) [can parallel with Phase 3, 4]
Phase 3,4,5 → Phase 6 (US-004: Verification)
Phase 2 → Phase 7 (US-005: TOML + docs) [can parallel with Phase 3-6]
Phase 2 → Phase 8 (US-006: Test support) [can parallel with Phase 3-7]
All phases → Phase 9 (Polish)
```

## Parallel Execution

After Phase 2 completes, the following can run in parallel:

**Parallel Group A** (different validators, different test sections):
- Phase 3 (US-001): Field validators — `T014-T019`
- Phase 4 (US-002): DummyAuth model validator — `T020-T021`
- Phase 5 (US-003): Crowd model validator — `T022-T024`

**Parallel Group B** (documentation, independent files):
- `T028` README.md update
- `T029` CLAUDE.md update
- `T030` Dockerfile update

## Implementation Strategy

**MVP (Recommended first pass)**: Phases 1-2 + Phase 3 (US-001)
- Gets the core config model working with basic validation
- All existing tests pass
- Validates that pydantic-settings TOML loading works

**Full delivery**: All phases 1-9

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase completion
- Stop at any checkpoint to validate independently
- The `tests/test_config_validation.py` file is shared across US-001, US-002, US-003, US-004, US-005 — tasks append to it sequentially
