# Contract: Error Responses

## Form Login Error Response (`POST {prefix}/login`)

### On Backend Failure

- **HTTP Status**: 503 Service Unavailable
- **Body**: Rendered `login.html` template with:
  - `error` = "Authentication service is temporarily unavailable. Please try again later."
  - `realm` = configured realm name
  - `target` = not required (form resubmission will re-provide)
- **Server Log**: ERROR level with full exception traceback

### On Wrong Credentials (unchanged)

- **HTTP Status**: 401 Unauthorized
- **Body**: Rendered `login.html` template with:
  - `error` = "Please check user name and password"

## Basic Auth Validation Error Response (`GET {prefix}/validate`)

### On Backend Failure

- **HTTP Status**: 503 Service Unavailable
- **Body**: Plain text "Authentication service unavailable"
- **Headers**: `Cache-Control: no-cache`
- **Server Log**: ERROR level with full exception traceback

### On Wrong Credentials (unchanged)

- **HTTP Status**: 401 Unauthorized
- **Body**: "Username/password failed"

## Security Contract

- Error responses MUST NOT contain: exception class names, stack traces, server hostnames, internal URLs, file paths
- The error message is a fixed string — no dynamic content from the exception is included in the response
