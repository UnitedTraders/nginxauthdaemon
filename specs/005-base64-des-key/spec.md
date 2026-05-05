# Feature Specification: Base64 DES Key Format

## Overview

The `des_key` configuration field currently requires an 8-byte binary value expressed as raw unicode escape sequences (e.g., `"\u00c8\u009a\u0017\u008f\u0017\u00d7\u0093:"`). This format is error-prone, difficult to generate, and unintuitive for operators managing config files. This feature changes the `des_key` format to accept a standard base64-encoded string that decodes to exactly 8 bytes of binary data.

## User Stories

- **US-001** (P1): As a system administrator, I want to specify the DES encryption key as a base64 string so that I can easily generate and manage it using standard tools (e.g., `openssl rand -base64 8` or `base64` command).
- **US-002** (P1): As a system administrator, I want a clear error message when my base64 key does not decode to exactly 8 bytes so that I can fix the configuration without guesswork.
- **US-003** (P2): As a developer deploying the daemon, I want the example configuration to show the new base64 format so that I can follow the correct pattern from the start.

## User Scenarios & Testing

### Scenario 1: Valid base64 key (happy path)

**Given** a TOML config file with `des_key = "yJoXjxfXkzo="` (a valid base64 string that decodes to 8 bytes)
**When** the application starts
**Then** the configuration loads successfully and session cookie encryption/decryption works correctly

### Scenario 2: Invalid base64 — wrong decoded length

**Given** a TOML config file with `des_key = "dGVzdA=="` (decodes to 4 bytes: "test")
**When** the application starts
**Then** startup fails with a validation error message stating that the decoded key must be exactly 8 bytes, and showing the actual decoded length

### Scenario 3: Invalid base64 — not valid base64 encoding

**Given** a TOML config file with `des_key = "not-valid-base64!!!"`
**When** the application starts
**Then** startup fails with a validation error message stating that the value is not valid base64

### Scenario 4: Default placeholder key rejected in production

**Given** a TOML config file that does not override `des_key` (uses the built-in default placeholder)
**When** the application starts in non-testing mode
**Then** startup fails with a validation error stating that `des_key` must be changed from the default placeholder value

### Scenario 5: Existing sessions remain valid after key format migration

**Given** session cookies encrypted with the same underlying 8-byte key (just expressed differently in config)
**When** the operator migrates from the old unicode-escape format to the equivalent base64 format
**Then** existing session cookies are still decrypted and validated correctly (because the underlying binary key is identical)

## Functional Requirements

- **FR-001**: The `des_key` config field must accept a base64-encoded string as its value.
- **FR-002**: At startup, the base64 string must be decoded to binary. The decoded value must be exactly 8 bytes. If not, a clear validation error must be raised.
- **FR-003**: If the `des_key` value is not valid base64, a clear validation error must be raised at startup.
- **FR-004**: The decoded 8-byte binary key must be used for DES-ECB encryption and decryption of session cookies (same cryptographic behavior as today, only the config representation changes).
- **FR-005**: The example configuration file must be updated to show the base64 format with a comment explaining how to generate a new key.
- **FR-006**: The default placeholder key in the codebase must be updated to base64 format.
- **FR-007**: The application must reject the default placeholder `des_key` at startup in non-testing mode, consistent with how `session_salt` is already validated. This prevents running production with a known key.

## Out of Scope

- Changing the encryption algorithm (DES-ECB remains as-is)
- Backward compatibility with the old unicode-escape format (this is a breaking config change; operators must convert their key)
- Automatic migration tooling for existing config files

## Success Criteria

### Measurable Outcomes

- **SC-001**: Operators can generate a valid DES key using a single standard shell command (e.g., `openssl rand -base64 8`) and paste it directly into the config file
- **SC-002**: Invalid key values (wrong length, bad base64) produce error messages that name the problem and state the exact requirement
- **SC-003**: All existing tests continue to pass after updating test fixtures to use the base64 format
- **SC-004**: Session cookie encryption/decryption behavior is identical to current behavior when the same underlying 8-byte key is used

## Assumptions

- Operators have access to standard base64 encoding tools (openssl, base64 command, Python, etc.)
- This is an acceptable breaking change to the config format; operators will update their config files during upgrade
- The old unicode-escape `des_key` format does not need to be supported alongside the new base64 format
- The underlying DES-ECB encryption mechanism and 8-byte key requirement are unchanged

## Clarifications

### Session 2026-05-05

- Q: Should the new base64 format also add a "reject default placeholder" guard (like `session_salt`)? → A: Yes, reject the default placeholder `des_key` in production (Option A)
