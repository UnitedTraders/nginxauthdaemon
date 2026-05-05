# Data Model: Base64 DES Key Format

## Modified Entity: AppConfig

| Field | Type | Default | Validation | Changed |
|-------|------|---------|------------|---------|
| `des_key` | `str` | `"yJoXjxfXkzo="` (placeholder) | Must be valid base64; decoded length must be exactly 8 bytes; must not equal default placeholder | Yes |

### Validation Rules

1. **Default placeholder rejection**: `des_key` must not equal `_DEFAULT_PLACEHOLDER_DES_KEY` (`"yJoXjxfXkzo="`)
2. **Valid base64**: `base64.b64decode(des_key)` must not raise an exception
3. **Decoded length**: `len(base64.b64decode(des_key)) == 8`

### Derived Values

| Key | Source | Description |
|-----|--------|-------------|
| `DES_KEY_BYTES` | `base64.b64decode(self.des_key)` | Decoded 8-byte binary, set in `to_flask_config()` for use by DES cipher |

## No New Entities

This feature modifies the representation of an existing config field. No new entities, relationships, or state transitions are introduced.
