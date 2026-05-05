# Research: Base64 DES Key Format

No NEEDS CLARIFICATION items were identified during planning. All design decisions are straightforward.

## Decision: Config field stores base64 string, Flask config gets decoded bytes

- **Decision**: The `des_key` pydantic field stores the base64 string as-is. The decoded bytes are computed once in `to_flask_config()` and stored as `DES_KEY_BYTES`.
- **Rationale**: Avoids decoding on every request. Keeps the pydantic model clean (string in, string validated). The Flask config dict carries the ready-to-use bytes.
- **Alternatives considered**:
  - Decode in the validator and store bytes in the model — rejected because pydantic fields work best with JSON-serializable types, and the TOML source is a string.
  - Decode at each DES.new() call — rejected for unnecessary repeated work.

## Decision: No backward compatibility with unicode-escape format

- **Decision**: The old `"\u00c8\u009a\u0017\u008f\u0017\u00d7\u0093:"` format is not supported alongside base64.
- **Rationale**: The old format is the problem being solved. Supporting both adds complexity for no benefit — this is an internal tool with controlled deployments.
- **Alternatives considered**:
  - Auto-detect format (try base64, fall back to raw_unicode_escape) — rejected because ambiguity between formats could mask misconfiguration.

## Decision: Default placeholder rejection follows session_salt pattern

- **Decision**: Add a guard in `validate_des_key` that rejects the default placeholder value, identical to how `validate_session_salt` works.
- **Rationale**: Prevents production use of the known default key. Consistent with existing security patterns in the codebase.
- **Alternatives considered**: None — this was explicitly requested in clarification.
