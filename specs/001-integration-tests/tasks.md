# Tasks: Integration Test Suite

**Input**: Design documents from `specs/001-integration-tests/`
**Prerequisites**: plan.md (required), spec.md (required)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Tests**: `tests/` at repository root
- **Config**: `requirements-test.txt` at repository root

---

## Phase 1: Setup

- [x] T001 Create test dependencies file at `requirements-test.txt` with pytest, pytest-cov, freezegun
- [x] T002 Create test configuration and fixtures in `tests/conftest.py` — Flask test client, app config overrides (DES_KEY, SESSION_SALT, AUTHENTICATOR, JWT_PRIVATE_KEY), helper functions for cookie creation and JWT decoding

## Phase 2: Foundational

No foundational tasks — all prerequisites are handled by the conftest fixtures.

## Phase 3: User Story 1 — Developer Runs Full Test Suite (P1)

> **Goal**: A single `pytest tests/` command runs all tests and reports results clearly.
> **Independent test**: Run `pytest tests/ -v` and confirm exit code 0 with all tests passing.

- [x] T003 [US1] Create `tests/__init__.py` (empty, marks tests as package)
- [x] T004 [US1] Create `tests/test_login_flow.py` with smoke test that Flask test client initializes and GET `/auth/login` returns 200

## Phase 4: User Story 2 — Validate Login Flow (P1)

> **Goal**: Full login → cookie → validate cycle works correctly.
> **Independent test**: Run `pytest tests/test_login_flow.py tests/test_validate.py -v` and verify all auth flow tests pass.

- [x] T005 [US2] Implement login success test in `tests/test_login_flow.py` — POST valid credentials (DummyAuthenticator: user==pass), verify 302 redirect, verify session cookie set, verify access token cookie set
- [x] T006 [US2] Implement login failure test in `tests/test_login_flow.py` — POST invalid credentials, verify 401 response, verify no cookies set, verify login form re-rendered with error
- [x] T007 [US2] Implement login redirect test in `tests/test_login_flow.py` — POST with target URL, verify redirect location matches target
- [x] T008 [P] [US2] Create `tests/test_validate.py` with valid session cookie test — login first, then GET `/auth/validate`, verify 200 response
- [x] T009 [US2] Implement missing cookie test in `tests/test_validate.py` — GET `/auth/validate` without cookies, verify 401 response with WWW-Authenticate header
- [x] T010 [US2] Implement Basic Auth success test in `tests/test_validate.py` — GET `/auth/validate` with valid Basic Auth header, verify 200 response and cookies set
- [x] T011 [US2] Implement Basic Auth failure test in `tests/test_validate.py` — GET `/auth/validate` with invalid Basic Auth header, verify 401 response

## Phase 5: User Story 3 — Validate Security Properties (P2)

> **Goal**: Session cookies are encrypted, tamper-resistant, and expire correctly.
> **Independent test**: Run `pytest tests/test_security.py -v` and verify all crypto/security tests pass.

- [x] T012 [P] [US3] Create `tests/test_security.py` with tampered cookie test — modify bytes of valid encrypted cookie, verify `/auth/validate` returns 401
- [x] T013 [US3] Implement wrong DES key test in `tests/test_security.py` — create cookie with different DES key, verify `/auth/validate` returns 401
- [x] T014 [US3] Implement expired session test in `tests/test_security.py` — use freezegun to advance time past 7-day expiry, verify `/auth/validate` returns 401 (note: if app doesn't check expiry in cookie, document this as a finding and test current behavior)
- [x] T015 [US3] Implement JWT claims verification test in `tests/test_security.py` — login, extract JWT cookie, decode with public key, verify `user_id` claim matches username, verify `exp` is set, verify RS256 algorithm

## Phase 6: User Story 4 — Validate Pluggable Authenticator (P2)

> **Goal**: Authenticator interface contract works correctly with pluggable backends.
> **Independent test**: Run `pytest tests/test_authenticator.py -v` and verify all authenticator tests pass.

- [x] T016 [P] [US4] Create `tests/test_authenticator.py` with DummyAuthenticator accept test — matching username/password returns True
- [x] T017 [US4] Implement DummyAuthenticator reject test in `tests/test_authenticator.py` — non-matching credentials return False
- [x] T018 [US4] Implement custom mock authenticator test in `tests/test_authenticator.py` — create a mock authenticator class, configure app to use it via dotted path, verify login uses custom authenticator
- [x] T019 [US4] Implement invalid authenticator path test in `tests/test_authenticator.py` — configure app with non-existent class path, verify login attempt raises clear error (ImportError or AttributeError)

## Phase 7: Polish & Cross-Cutting

- [x] T020 Run full test suite with `pytest tests/ -v --tb=short` and verify all tests pass
- [x] T021 Run `pytest tests/ --cov=nginxauthdaemon --cov-report=term-missing` and document coverage in a comment at top of `tests/conftest.py`

---

## Dependencies

```
T001 → T002 → T003/T004 → T005..T011, T012..T015, T016..T019 → T020 → T021
```

- Phase 1 (Setup) blocks all other phases
- Phase 3 (US1 smoke test) validates infrastructure before deeper tests
- Phase 4, 5, 6 (US2, US3, US4) are independent of each other after Phase 3
- Phase 7 (Polish) requires all story phases complete

## Parallel Execution

### Within Phase 4 (US2):
- T008 can run in parallel with T005-T007 (separate file)

### Across Phases 4-6:
- T012 (US3) can start in parallel with T008 (US2) — separate files
- T016 (US4) can start in parallel with T008 (US2) and T012 (US3) — separate files

### Team Strategy:
- Developer A: Phase 4 (login flow + validate)
- Developer B: Phase 5 (security tests)
- Developer C: Phase 6 (authenticator tests)
- All converge at Phase 7

## Implementation Strategy

1. **MVP (Phase 1-4)**: Setup + login flow + validate = proves the core auth contract works
2. **Security hardening (Phase 5)**: Crypto verification builds confidence in the security boundary
3. **Extensibility proof (Phase 6)**: Authenticator contract tests enable safe future backend additions
4. **Polish (Phase 7)**: Full suite validation and coverage reporting

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each phase or logical group
- The spec does not request TDD — tests ARE the feature, so all tasks are test-writing tasks
