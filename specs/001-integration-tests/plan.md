# Implementation Plan: Integration Test Suite

## Technical Context

| Aspect | Detail |
|--------|--------|
| Language | Python 3.9 |
| Framework | Flask 2.3.2 (test_client for integration testing) |
| Test framework | pytest + pytest-cov |
| Crypto | pycryptodome 3.19.1 (DES-ECB), PyJWT 2.4.0 (RS256) |
| Auth interface | `Authenticator.authenticate(username, password) -> bool` |
| Entry point | `nginxauthdaemon:app` (Flask WSGI app) |
| Cookie scheme | DES-ECB encrypted, base64-encoded, salt-appended plaintext |
| JWT scheme | RS256, claims: jti, iat, nbf, iss, exp, user_id, typ |
| Routes | `{prefix}/login` (GET/POST), `{prefix}/validate` (GET) |
| Config prefix | `AUTH_URL_PREFIX` defaults to `/auth` |

**Unknowns**: None — the codebase is small and fully inspected.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security-First | Compliant | Tests use hardcoded test secrets, not production values. RSA key from DefaultConfig is a dev key already in source. |
| II. Explicit Configuration | Compliant | Test config overrides via `app.config` in fixtures |
| III. Pluggable Architecture | Compliant | Tests verify authenticator contract with DummyAuthenticator + mock |
| IV. Defensive Coding | Compliant | Tests cover malformed cookies, invalid class paths, auth failures |
| V. Minimal Dependencies | Compliant | Only adds pytest + pytest-cov as test dependencies |

No violations. No complexity tracking needed.

## Research Summary

No external research needed. The project is self-contained:

- **Flask test_client**: Built-in, provides cookie jar persistence across requests
- **DES encryption**: Test roundtrip uses same `create_session_cookie`/`decode_session_cookie` functions
- **JWT verification**: Use `jwt.decode()` with the public key derived from the test private key
- **Authenticator loading**: `importlib` + dotted path — testable by passing invalid paths

## Data Model

No new persistent data. Test artifacts:

| Entity | Purpose |
|--------|---------|
| Test RSA keypair | Fixture-provided private key (reuse DefaultConfig key) + derived public key for JWT verification |
| Test DES key | 8-byte key from DefaultConfig (`'\xc8\x9a\x17\x8f\x17\xd7\x93:'`) |
| Test session salt | String from DefaultConfig (`"3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="`) |

## Architecture Decision

**Single-project structure** — tests live at repository root alongside the application:

```
nginxauthdaemon/          # existing application code (unchanged)
tests/
├── conftest.py           # pytest fixtures: Flask test client, test config
├── test_login_flow.py    # US1+US2: login, cookie setting, redirects
├── test_validate.py      # US2: session validation via cookie and Basic Auth
├── test_security.py      # US3: crypto properties, tamper detection, expiry
└── test_authenticator.py # US4: pluggable authenticator contract
requirements-test.txt     # test-only dependencies
```

**Structure Decision**: Tests in `tests/` at repo root. One file per user story grouping. Shared fixtures in `conftest.py`. No test utilities package needed — the test surface is small.

## Design Decisions

1. **Use DefaultConfig secrets directly** — they're already committed dev/example keys. No need to generate separate test keys.

2. **Flask test_client with cookie jar** — provides HTTP-level integration testing without starting a server. Cookies persist across requests within a session, enabling login→validate flow testing.

3. **No mocking of crypto internals** — tests call real DES/JWT code paths to verify actual encryption behavior. Only the Crowd authenticator needs mocking (and we test with DummyAuthenticator instead).

4. **Tamper tests via direct byte manipulation** — modify encrypted cookie bytes to verify rejection, rather than trying to encrypt with wrong parameters.

5. **Time-based expiry** — use `freezegun` or `unittest.mock.patch` on `time.time()` to simulate expired sessions without waiting.

## Complexity Tracking

No violations to justify.
