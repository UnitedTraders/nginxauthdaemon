# Tasks: Auth Server Error Handling

**Input**: Design documents from `specs/004-auth-error-handling/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Explicitly requested in spec (US-004). Test tasks included.

**Organization**: Tasks grouped by user story. US-001 and US-002 are tightly coupled (same code change) and grouped together. US-004 (tests) gets its own phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

> No project setup needed — modifying existing files only.

- [x] T001 Review current error paths in `nginxauthdaemon/nginxauthdaemon.py` lines 118-163 to confirm both `show_login()` and `validate()` call `get_authenticator().authenticate()` without exception handling

---

## Phase 2: US-001 + US-002 — Form Login Error Handling & Logging

> **Goal**: When the auth backend raises an exception during form login, catch it, log it, and show the user a service unavailable error on the login page with HTTP 503.

- [x] T002 [US1] Add try/except around `get_authenticator().authenticate(username, password)` in `show_login()` POST handler in `nginxauthdaemon/nginxauthdaemon.py`. On exception: log with `current_app.logger.exception()`, return `render_template('login.html', realm=..., error="Authentication service is temporarily unavailable. Please try again later."), 503`
- [x] T003 [US2] Verify the `current_app.logger.exception()` call in `show_login()` includes the full traceback in `nginxauthdaemon/nginxauthdaemon.py` (exception() automatically includes traceback)

---

## Phase 3: US-003 — Basic Auth Validate Error Handling

> **Goal**: When the auth backend raises an exception during Basic Auth validation, catch it, log it, and return HTTP 503 instead of 500.

- [x] T004 [US3] Add try/except around `get_authenticator().authenticate(...)` in `validate()` handler in `nginxauthdaemon/nginxauthdaemon.py`. On exception: log with `current_app.logger.exception()`, return `make_response("Authentication service unavailable", 503)` with `Cache-Control: no-cache` header

---

## Phase 4: US-004 — Test Coverage

> **Goal**: Add automated tests that verify backend failure scenarios return proper error responses, not 500s.

- [x] T005 [P] [US4] Create test file `tests/test_auth_errors.py` with test: form login POST with `authenticate()` raising `Exception` returns HTTP 503 and response body contains "temporarily unavailable"
- [x] T006 [P] [US4] Add test in `tests/test_auth_errors.py`: form login POST with `authenticate()` raising `ConnectionError` returns HTTP 503 and login page is rendered (contains form elements)
- [x] T007 [P] [US4] Add test in `tests/test_auth_errors.py`: Basic Auth validate GET with `authenticate()` raising `Exception` returns HTTP 503 (not 500)
- [x] T008 [P] [US4] Add test in `tests/test_auth_errors.py`: error response body does NOT contain the exception message string (e.g., "Connection refused" should not appear in HTML response)
- [x] T009 [P] [US4] Add test in `tests/test_auth_errors.py`: verify the wrong-credentials path still returns 401 with "Please check user name and password" (regression test for existing behavior)

---

## Phase 5: Final Verification

> **Goal**: Confirm no regressions and all acceptance criteria met.

- [x] T010 Run full test suite with `pytest tests/ -v` to confirm all tests pass (existing 55 + new tests)
- [x] T011 Verify no 500 error paths remain for auth backend failures by reviewing `nginxauthdaemon/nginxauthdaemon.py` — all `authenticate()` calls must be wrapped in try/except

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Form Login Error Handling)
                → Phase 3 (Basic Auth Error Handling)
Phase 2 + Phase 3 → Phase 4 (Tests)
All Phases → Phase 5 (Final Verification)
```

## User Story Dependency Graph

```
US-001 + US-002 (Form Login) ─── independent
US-003 (Basic Auth) ─── independent
US-004 (Tests) ─── depends on US-001, US-002, US-003 implementation
```

## Implementation Strategy

### MVP First

1. Complete Phase 2 (form login error handling) → most visible user impact
2. Complete Phase 3 (Basic Auth) → completes all error paths
3. Complete Phase 4 (tests) → validates everything
4. Phase 5 (verification) → final pass

### Parallel Opportunities

- T005-T009 are all in the same file but are independent test functions — they can be written together in one pass
- Phase 2 and Phase 3 modify the same file but different functions — can be done in one pass

---

## Notes

- [P] tasks = different files, no dependencies
- US-001 and US-002 are in the same phase because they're the same code change (catch + log)
- All T005-T009 tests use `unittest.mock.patch` to make `authenticate()` raise exceptions
- Commit after Phase 3 (implementation complete) and after Phase 4 (tests complete)
