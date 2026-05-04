# Feature Specification: Auth Server Error Handling

**Feature**: Gracefully handle authentication backend failures and display user-friendly error messages
**Date**: 2026-05-04
**Status**: Draft

## Overview

When the configured authentication backend (e.g., Crowd server) is unreachable or returns an unexpected error, the login page currently shows a raw 500 Internal Server Error. This provides no useful information to the user and exposes internal system details. The system should catch backend failures and display a clear, actionable error message on the login page.

## User Stories

### US-001: Friendly Error on Auth Backend Failure (P1)
**As a** user attempting to log in,
**I want** to see a clear message like "Authentication service is temporarily unavailable" when the auth backend is down,
**So that** I understand the problem is not with my credentials and can try again later.

**Acceptance Criteria**:
- When the authentication backend is unreachable, the login page displays an error message indicating the service is unavailable
- The error message is distinct from the "wrong credentials" message so users do not confuse the two
- The login form remains functional and ready for retry
- The page returns an appropriate HTTP status code (not 500)

### US-002: Auth Backend Error Logging (P1)
**As a** system administrator,
**I want** authentication backend failures to be logged with sufficient detail,
**So that** I can diagnose connectivity issues without needing to reproduce them.

**Acceptance Criteria**:
- When the auth backend fails, the actual error details (connection refused, timeout, etc.) are logged server-side
- The log entry includes enough context to identify the failure point
- Internal error details are never exposed to the end user

### US-003: Consistent Error Handling Across Auth Paths (P2)
**As a** system administrator,
**I want** auth backend failures handled consistently for both form login and Basic Auth validation,
**So that** the system behaves predictably regardless of how the user authenticates.

**Acceptance Criteria**:
- Form login (POST to `/auth/login`): returns the login page with a service unavailable error message
- Basic Auth validation (GET `/auth/validate`): returns an appropriate HTTP error response (not 500)
- Both paths log the underlying error

### US-004: Test Coverage for Error Scenarios (P1)
**As a** developer,
**I want** automated tests covering auth backend failure scenarios,
**So that** regressions in error handling are caught before deployment.

**Acceptance Criteria**:
- Tests verify that a backend exception during form login returns the login page with an error message (not a 500)
- Tests verify that a backend exception during Basic Auth validation returns an appropriate HTTP error (not a 500)
- Tests verify that the error message shown to the user does not contain internal system details

## Functional Requirements

### FR-001: Catch Backend Exceptions During Login
When the authentication backend raises any exception during a login attempt, the system must catch it, log it, and return the login page with a user-friendly error message and an appropriate HTTP status code (503 Service Unavailable).

### FR-002: Catch Backend Exceptions During Validation
When the authentication backend raises any exception during Basic Auth validation, the system must catch it, log it, and return an appropriate HTTP error response (503) instead of an unhandled 500.

### FR-003: User-Facing Error Message
The error message shown to the user must clearly indicate a service availability issue (e.g., "Authentication service is temporarily unavailable. Please try again later."). It must not contain stack traces, hostnames, or internal details.

### FR-004: Server-Side Error Logging
The caught exception must be logged at an appropriate severity level, including the exception type and message. This enables administrators to diagnose issues from logs.

### FR-005: Separation of Error Types
The "service unavailable" error must be visually and textually distinct from the "wrong credentials" error, so users can tell whether they need to correct their input or wait and retry.

## User Scenarios & Testing

### Scenario 1: Auth Backend Down During Form Login
1. User navigates to the login page
2. User enters valid credentials and submits
3. The auth backend is unreachable (connection refused, timeout, DNS failure)
4. The login page reloads with error: "Authentication service is temporarily unavailable. Please try again later."
5. HTTP status code is 503
6. The form fields are ready for retry

### Scenario 2: Auth Backend Down During Basic Auth
1. A client sends a request with Basic Auth credentials to a protected resource
2. nginx forwards the validation subrequest to `/auth/validate`
3. The auth backend is unreachable
4. The daemon returns 503 (not 500)
5. The error is logged server-side

### Scenario 3: Auth Backend Recovers
1. The auth backend was down and the user saw the service unavailable message
2. The auth backend comes back online
3. The user retries login with valid credentials
4. Login succeeds normally — no stale error state

### Scenario 4: Wrong Credentials vs Service Down
1. User enters wrong credentials → sees "Please check user name and password" (existing behavior, unchanged)
2. Auth backend is down → sees "Authentication service is temporarily unavailable" (new behavior)
3. The two messages are distinct

## Success Criteria

### Measurable Outcomes
- **SC-001**: Authentication backend failures never result in a 500 Internal Server Error being shown to the user
- **SC-002**: 100% of auth backend failure scenarios are covered by automated tests
- **SC-003**: Users can distinguish between "wrong credentials" and "service unavailable" errors on the login page
- **SC-004**: All existing tests continue to pass without modification

## Assumptions

- The authentication backend may fail due to network issues (connection refused, timeout, DNS failure) or unexpected server errors
- The existing error display mechanism on the login page (the `error` template variable) is sufficient for showing service unavailable messages
- No retry logic or circuit breaker is needed — the user manually retries by resubmitting the form
- The scope is limited to catching and displaying errors — no monitoring, alerting, or health check endpoints are included
