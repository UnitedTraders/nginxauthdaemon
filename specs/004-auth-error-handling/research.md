# Research: Auth Server Error Handling

## R1: Exception Sources in Auth Flow

**Decision**: Wrap `get_authenticator().authenticate()` calls with try/except in both route handlers.
**Rationale**: There are exactly two call sites where the auth backend is invoked:
1. `show_login()` at line 127: `get_authenticator().authenticate(username, password)` — form login POST
2. `validate()` at line 152: `get_authenticator().authenticate(user_and_password[0], user_and_password[1])` — Basic Auth

Additionally, `get_authenticator()` itself (line 19-29) can fail during authenticator instantiation — e.g., `CrowdAuthenticator.__init__` creates a `crowd.CrowdServer` which could fail if config is wrong at runtime.

The `CrowdAuthenticator.authenticate()` calls `self._cs.auth_user()` which makes HTTP requests to the Crowd server. This can raise `ConnectionError`, `Timeout`, `requests.exceptions.RequestException`, or any subclass thereof.

**Alternatives considered**:
- Wrapping at the `Authenticator.authenticate()` level: Would hide errors from the route handler, making it impossible to distinguish "auth failed" from "service down". Rejected.
- Flask error handler (`@app.errorhandler(500)`): Catches all 500s globally but can't provide context-specific error messages (login page vs validate endpoint). Rejected as sole mechanism — but could be a fallback safety net.

## R2: HTTP Status Code for Service Unavailable

**Decision**: Return HTTP 503 Service Unavailable.
**Rationale**: 503 is the standard HTTP status code for "the server is currently unable to handle the request due to temporary overloading or maintenance." This accurately describes an unreachable auth backend. It also signals to nginx/proxies that the failure is transient, unlike 500 which suggests a server bug.
**Alternatives considered**:
- 500 Internal Server Error: The current (broken) behavior. Doesn't communicate transience. Rejected.
- 502 Bad Gateway: Semantically close but implies this server is a proxy, which is technically true but 503 is more conventional for "dependency down". Rejected.

## R3: Error Logging Strategy

**Decision**: Use `app.logger.exception()` which logs at ERROR level and includes the full traceback.
**Rationale**: Flask's built-in logger with `exception()` captures the traceback automatically. This gives administrators the full error context (connection refused, timeout, DNS failure) without any additional dependencies.
**Alternatives considered**:
- `app.logger.error(str(e))`: Loses the traceback. Rejected.
- Custom structured logging: Over-engineering for this project's scope. Rejected.

## R4: Error Message Wording

**Decision**: Use "Authentication service is temporarily unavailable. Please try again later."
**Rationale**: Clear, actionable, and distinct from the existing "Please check user name and password" message. Does not expose internal details (no server names, URLs, or stack traces). The word "temporarily" signals the issue is transient.

## R5: Test Strategy

**Decision**: Mock the authenticator's `authenticate()` method to raise exceptions, then verify response status and content.
**Rationale**: Tests already use DummyAuthenticator. By patching `authenticate()` to raise `Exception` (or specific subtypes), we can simulate backend failures without needing a real Crowd server. This tests the error handling in isolation.
**Test cases**:
1. Form login with backend exception → 503 + error message on login page
2. Basic Auth validate with backend exception → 503 response
3. Verify error message text does not contain exception details
4. Verify authenticator instantiation failure is also caught
