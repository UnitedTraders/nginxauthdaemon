# Implementation Plan: Auth Server Error Handling

**Branch**: `004-auth-error-handling` | **Date**: 2026-05-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/004-auth-error-handling/spec.md`

## Technical Context

| Aspect | Detail |
|--------|--------|
| Language | Python 3.13 |
| Framework | Flask 3.1.3 |
| Auth backend | Crowd library (`crowd.CrowdServer.auth_user()`) |
| Error source | `CrowdAuthenticator.authenticate()` raises on network failure |
| Affected routes | `show_login()` (POST), `validate()` (GET) |
| Test framework | pytest with Flask test client |
| Existing tests | 55 passing |

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security-First | PASS | Error responses expose no internal details. Fixed error message string. |
| II. Explicit Configuration | N/A | No config changes. |
| III. Pluggable Architecture | PASS | Error handling wraps the `authenticate()` interface — works with any authenticator. |
| IV. Defensive Coding | PASS | This feature directly implements defensive coding: catching external service failures, returning appropriate HTTP codes, logging errors. |
| V. Minimal Dependencies | PASS | No new dependencies. Uses Flask's built-in logger. |

## Implementation Strategy

Two route handlers need try/except blocks around `get_authenticator().authenticate()` calls. One new test file.

### Change 1: `show_login()` route (form login)

Wrap the authenticate call at line 127 in a try/except. On exception: log with `app.logger.exception()`, return login template with service unavailable error message, HTTP 503.

### Change 2: `validate()` route (Basic Auth)

Wrap the authenticate call at line 152 in a try/except. On exception: log with `app.logger.exception()`, return 503 plain text response with `Cache-Control: no-cache`.

### Change 3: Tests

New test file `tests/test_auth_errors.py` with tests that patch `authenticate()` to raise exceptions and verify:
- Form login returns 503 with error message
- Validate returns 503
- Error message doesn't contain exception details
- Authenticator instantiation failure is handled

## File Change Summary

| File | Action | Description |
|------|--------|-------------|
| `nginxauthdaemon/nginxauthdaemon.py` | Modify | Add try/except in `show_login()` and `validate()` |
| `tests/test_auth_errors.py` | Create | Backend failure test scenarios |

## Project Structure

No structural changes. Two files touched.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
