# Data Model: Auth Server Error Handling

This feature involves no persistent data model changes. It modifies the error handling behavior of two existing route handlers.

## Affected Endpoints

| Endpoint | Method | Current Behavior on Backend Failure | New Behavior |
|----------|--------|-------------------------------------|-------------|
| `{prefix}/login` | POST | Unhandled 500 | 503 + login page with error message |
| `{prefix}/validate` | GET | Unhandled 500 | 503 response with error text |

## Error States

| State | HTTP Status | User-Facing Message | Logged |
|-------|-------------|---------------------|--------|
| Wrong credentials | 401 | "Please check user name and password" | No (existing) |
| Backend unavailable | 503 | "Authentication service is temporarily unavailable. Please try again later." | Yes (exception + traceback) |
| Valid credentials | 302 (redirect) | N/A | No (existing) |

## Files Affected

| File | Change Type | Description |
|------|-------------|-------------|
| `nginxauthdaemon/nginxauthdaemon.py` | Modify | Add try/except around authenticate() calls in both routes |
| `tests/test_auth_errors.py` | Create | New test file for backend failure scenarios |
