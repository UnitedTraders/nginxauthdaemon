# Config Format Contract: des_key

## TOML Format

```toml
# DES encryption key (base64-encoded, must decode to exactly 8 bytes)
# Generate with: openssl rand -base64 8
des_key = "yJoXjxfXkzo="
```

## Validation Contract

| Check | Rule | Error message |
|-------|------|---------------|
| Not default placeholder | `des_key != "yJoXjxfXkzo="` | `des_key must be changed from the default placeholder value` |
| Valid base64 | `base64.b64decode(v)` succeeds | `des_key is not valid base64` |
| Decoded length | `len(decoded) == 8` | `des_key must decode to exactly 8 bytes, got {n}` |

## Migration from Old Format

Old format (unicode escape in TOML):
```toml
des_key = "\u00c8\u009a\u0017\u008f\u0017\u00d7\u0093:"
```

To convert an existing key to base64:
```python
import base64
old_key = '\xc8\x9a\x17\x8f\x17\xd7\x93:'
print(base64.b64encode(old_key.encode('raw_unicode_escape')).decode())
# Output: yJoXjxfXkzo=
```

To generate a new random key:
```bash
openssl rand -base64 8
```
