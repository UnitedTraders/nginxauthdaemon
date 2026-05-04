# Feature: Integration Test Suite

## Overview

Add a working integration test suite to the nginxauthdaemon project that validates the complete authentication flow end-to-end using Flask's test client. The test suite verifies session cookie creation, encryption/decryption, JWT token issuance, route protection, and authenticator integration — providing confidence that the daemon behaves correctly as a unified system.

## User Scenarios & Testing

### US1: Developer Runs Full Test Suite (P1)

**As a** developer maintaining nginxauthdaemon,
**I want to** run a single command that executes all integration tests,
**So that** I can verify the authentication system works correctly after making changes.

**Acceptance Criteria:**
- Running `pytest tests/` from the project root executes all integration tests
- Tests complete successfully on a clean checkout with only project dependencies installed
- Tests do not require any external services (no Crowd server, no nginx, no network)
- Test output clearly indicates which authentication flows passed or failed
- Tests run on Python 3.9

### US2: Developer Validates Login Flow (P1)

**As a** developer,
**I want to** verify that the login → session cookie → validate cycle works correctly,
**So that** I know the core authentication contract with nginx is maintained.

**Acceptance Criteria:**
- Test proves that valid credentials produce a session cookie and JWT access token
- Test proves that invalid credentials do not produce cookies and re-render the login form
- Test proves that a valid session cookie passes `/auth/validate` (returns 200)
- Test proves that a missing or tampered cookie fails `/auth/validate` (returns 401)
- Test proves that Basic Auth header is accepted as an alternative to cookie-based sessions

### US3: Developer Validates Security Properties (P2)

**As a** developer,
**I want to** verify that session cookies are properly encrypted and tamper-resistant,
**So that** I can trust the security boundary is maintained.

**Acceptance Criteria:**
- Test proves that a modified cookie payload is rejected (salt verification fails)
- Test proves that a cookie encrypted with a different DES key is rejected
- Test proves that expired sessions are rejected
- Test proves that the JWT access token contains the expected claims (user_id, expiry)

### US4: Developer Validates Pluggable Authenticator (P2)

**As a** developer adding a new authenticator backend,
**I want to** verify that the authenticator interface contract works correctly,
**So that** I can confirm new backends integrate without modifying core code.

**Acceptance Criteria:**
- Test proves that DummyAuthenticator accepts matching username/password
- Test proves that DummyAuthenticator rejects non-matching credentials
- Test proves that a custom mock authenticator can be plugged in via configuration
- Test proves that an invalid authenticator class path causes a clear startup error

## Functional Requirements

### FR-1: Test Infrastructure

- The project MUST include a `tests/` directory at the repository root
- A `tests/conftest.py` MUST provide reusable pytest fixtures (Flask test client, test configuration)
- Test configuration MUST use deterministic, hardcoded secrets (not production values)
- Tests MUST be runnable with `pytest tests/` without additional setup beyond `pip install`
- A `requirements-test.txt` file MUST list test dependencies (pytest, pytest-cov)

### FR-2: Authentication Flow Tests

- Tests MUST cover the complete login flow: POST credentials → receive cookies → validate session
- Tests MUST verify both success and failure paths for credential validation
- Tests MUST verify redirect behavior after successful login (redirect to target URL)
- Tests MUST verify that the login page renders correctly on GET request

### FR-3: Session Cookie Tests

- Tests MUST verify DES encryption/decryption roundtrip for session cookies
- Tests MUST verify salt-based integrity checking rejects tampered cookies
- Tests MUST verify that cookies from a different key/salt combination are rejected
- Tests MUST verify session expiry enforcement

### FR-4: JWT Token Tests

- Tests MUST verify that a JWT access token is set alongside the session cookie
- Tests MUST verify the JWT contains the correct `user_id` claim
- Tests MUST verify the JWT is signed with RS256

### FR-5: Basic Auth Tests

- Tests MUST verify that valid Basic Auth credentials pass `/auth/validate`
- Tests MUST verify that invalid Basic Auth credentials fail `/auth/validate`

### FR-6: Authenticator Contract Tests

- Tests MUST verify the DummyAuthenticator contract (username == password)
- Tests MUST verify that a custom authenticator class can be loaded via config
- Tests MUST verify error handling for invalid authenticator class paths

## Success Criteria

- All integration tests pass on a clean environment with Python 3.9 and declared dependencies
- Tests execute without requiring network access or external services
- A developer can run the full suite and get pass/fail results within 30 seconds
- Test coverage includes the primary authentication flow (login, validate, token)
- Tests catch regressions in cookie encryption, JWT signing, and authenticator loading

## Assumptions

- Python 3.9 is the target runtime for test execution
- No external services are required — all authenticator calls are handled via DummyAuthenticator or mocks
- The existing Flask app structure (`nginxauthdaemon:app`) is testable via Flask's `test_client()` without modification
- RSA key pair for JWT testing will be generated as a test fixture (not using production keys)
- The project does not currently have any tests, so this is a greenfield addition
