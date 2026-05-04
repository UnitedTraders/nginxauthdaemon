<!--
Sync Impact Report
- Version change: none → 1.0.0
- Added principles: Security-First, Explicit Configuration, Pluggable Architecture, Defensive Coding, Minimal Dependencies
- Added sections: Technology Standards, Development Workflow
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes needed (generic)
  - .specify/templates/spec-template.md ✅ no changes needed (generic)
  - .specify/templates/tasks-template.md ✅ no changes needed (generic)
- Follow-up TODOs: none
-->

# nginxauthdaemon Constitution

## Core Principles

### I. Security-First

All authentication and session management code MUST treat security as the
primary concern. Specifically:

- Secrets (DES keys, salts, private keys) MUST NEVER appear in source control
  or log output.
- Cryptographic operations MUST use well-audited libraries (pycryptodome, PyJWT)
  and MUST NOT implement custom crypto algorithms.
- Cookie values MUST be encrypted and include integrity verification (salt check).
- JWT tokens MUST use asymmetric signing (RS256) to allow verification without
  exposing the private key.
- All user-supplied input (credentials, redirect URLs, headers) MUST be validated
  before use. Redirect targets MUST be restricted to prevent open-redirect
  vulnerabilities.
- Session expiry MUST be enforced server-side; client-controlled expiry alone is
  insufficient.

**Rationale**: This daemon is the trust boundary for all protected upstream
services. A single vulnerability here compromises the entire system.

### II. Explicit Configuration

All configurable behavior MUST be driven by external configuration loaded via
the `DAEMON_SETTINGS` environment variable. Specifically:

- `config.py:DefaultConfig` defines all defaults with secure-by-default values
  where possible.
- Secrets MUST NOT have usable defaults — the application MUST fail to start if
  critical secrets (`DES_KEY`, `SESSION_SALT`, `JWT_PRIVATE_KEY`) are left at
  placeholder values.
- Configuration keys MUST be documented in CLAUDE.md and example.cfg.
- Environment-specific values (URLs, ports, cookie domains) MUST be configurable
  without code changes.

**Rationale**: Deployment across different environments (dev, staging, production)
requires clear separation of config from code. Flask's config-from-envvar
pattern supports this natively.

### III. Pluggable Architecture

Authentication backends MUST be pluggable via the `AUTHENTICATOR` config setting.
Specifically:

- Authenticators MUST implement the `Authenticator` base class from `auth.py`.
- The `authenticate(username, password) -> bool` contract MUST be the sole
  interface between the daemon and any backend.
- New authenticator implementations MUST be addable without modifying core
  daemon code — only configuration changes required.
- Each authenticator module MUST be independently testable with mocked external
  dependencies.

**Rationale**: The daemon supports multiple identity providers (Crowd, LDAP,
custom). Loose coupling ensures new backends do not introduce regressions in
core session handling.

### IV. Defensive Coding

All code MUST handle failure cases explicitly. Specifically:

- External service calls (Crowd API, etc.) MUST have timeouts and error handling.
  Network failures MUST NOT crash the daemon.
- Flask route handlers MUST return appropriate HTTP status codes (200, 401, 403,
  302) — never unhandled 500 errors for expected conditions.
- Cookie parsing/decryption MUST gracefully handle malformed or tampered data by
  treating it as an invalid session (return 401), not by raising exceptions.
- Import and instantiation of the configured authenticator class MUST fail fast
  at startup with a clear error message if the class path is invalid.

**Rationale**: As an auth gateway, availability and predictable behavior under
error conditions are critical. Silent failures or crashes leave upstream
services unprotected or inaccessible.

### V. Minimal Dependencies

The dependency set MUST remain minimal and each dependency MUST be justified.
Specifically:

- Production dependencies are limited to: Flask, pycryptodome, PyJWT, gunicorn,
  eventlet, and authenticator-specific libraries (e.g., Crowd).
- Adding a new dependency MUST be justified by a clear need that cannot be met
  with the standard library or existing dependencies.
- Dependencies MUST be pinned to specific versions in requirements files to
  ensure reproducible builds.
- Security vulnerabilities in dependencies MUST be addressed promptly via
  version bumps (as evidenced by existing Snyk/Dependabot workflow).

**Rationale**: A security-critical service has a smaller attack surface with
fewer dependencies. Each additional package is a potential supply-chain risk.

## Technology Standards

- **Language**: Python 3.x (compatible with Docker base image python:3.x-slim)
- **Framework**: Flask 2.x with WSGI deployment
- **Server**: gunicorn with eventlet async workers
- **Crypto**: pycryptodome for symmetric encryption, PyJWT for token handling
- **Containerization**: Docker with multi-stage builds where applicable
- **Proxy integration**: nginx `auth_request` module or HAProxy equivalent
- **Code style**: PEP 8 compliance; imports grouped (stdlib, third-party, local)
- **Type hints**: Encouraged for new code; not retroactively required for
  existing code

## Development Workflow

- All changes MUST be submitted via pull requests against the `master` branch.
- Security-sensitive changes (crypto, cookie handling, JWT logic) MUST receive
  explicit review from a team member familiar with the auth flow.
- Configuration changes MUST include corresponding updates to `example.cfg` and
  CLAUDE.md documentation.
- Docker builds MUST pass (`docker build .`) before merge.
- Dependency updates MUST be tested with a full application startup to verify
  compatibility (no test suite currently exists; manual or smoke-test
  verification is acceptable until tests are added).

## Governance

This constitution supersedes informal practices and MUST be consulted when
making architectural decisions. Amendments require:

1. A pull request modifying this file with rationale in the PR description.
2. Approval from at least one maintainer.
3. Version bump following semantic versioning (MAJOR for principle
   removals/redefinitions, MINOR for additions, PATCH for clarifications).

All code reviews SHOULD verify compliance with these principles. Complexity
beyond what is described here MUST be justified in the PR description.

Refer to `CLAUDE.md` for runtime development guidance and command reference.

**Version**: 1.0.0 | **Ratified**: 2026-05-04 | **Last Amended**: 2026-05-04
