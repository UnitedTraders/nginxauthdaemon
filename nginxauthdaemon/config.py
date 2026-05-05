import base64
import os
import sys
import importlib
from enum import Enum
from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource


# Default placeholder salt — config validation rejects this in production
_DEFAULT_PLACEHOLDER_SALT = "3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="

# Default placeholder DES key — config validation rejects this in production
_DEFAULT_PLACEHOLDER_DES_KEY = "yJoXjxfXkzo="

# Default placeholder RSA key — config validation rejects this in production
_DEFAULT_PLACEHOLDER_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCwvaYt11Xpp3CaEtSfyMQrKGMbmPBUJ0vs8vQk1ukkkaSbYOQt
Sii9hQrUjz4BJjHhxgc0lZHLPnbSdU0j5f12Ug/dNxSQ+gj015K6DtZp9Ltcoa5h
BbHb2+C9elCha9Kp8QpLH7PYz8L/Z2/YRlgodT1aqgczrsc0vH/EVzKCjQIDAQAB
AoGBAKX48t2JonxRaUTG+jUy7EU7IBcCgG4GmR5i6TLPPxHAU7w2ORDu22NeVNVX
zvp1S9KhjJKtAsTCXAM3dMGJcYLjPWUp9owrLKoevzH4mmsv2/4cDRKh79Img3MQ
eIk570oe9jJg3C9MmPXbR/B8EB1G+97M6FnWJrzb4fU1JClhAkEA4hVzFW4dvLmW
1CtcPIhJsx9fvCeFyoQAs4b4FWmqY7BYkSRVLfeSllI2YvUq58Ufda7/njbUa1Ki
OHfnK/MMDwJBAMggtviBHwIbVVBVsYOWOLSVtPwbz0nxpBdSpKqixfif9Hj0XTTt
fYcKnVcmAT5+KjZkTX/JsEyaqXdKYVDP26MCQHRi6m3b1D81o2nyMHeRCa/GtPgd
uIh60Ambr9cGIItVWyLM+3TAgJwWEp167O2H0xw4TKtcOppNXemIAF/lrQ0CQFaB
DZXM+kJG3lGjON/QByLHsztmKeukb3FFX7gCM+CMA3hk6AUAwsmkZO5OlysUDdsE
8BrUa0gxch8GH5p2vlECQAmlBjmwbYOJ9lXWppKlUDbtk9DFm40YRB83ysZMZoUZ
C4cnTxWQ/CrQSwiSHy5Xr13jVLhVgmtudfJsfzUgxw8=
-----END RSA PRIVATE KEY-----
"""

AUTHENTICATOR_MAP = {
    "crowd": "nginxauthdaemon.crowdauth.CrowdAuthenticator",
    "dummy": "nginxauthdaemon.auth.DummyAuthenticator",
}


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=os.environ.get('DAEMON_SETTINGS', 'config.toml'),
    )

    realm_name: str = "Realm"
    session_cookie: str = "auth_session"
    target_header: str = "X-Target"
    session_salt: str = _DEFAULT_PLACEHOLDER_SALT
    des_key: str = _DEFAULT_PLACEHOLDER_DES_KEY
    authenticator: str = "crowd"
    jwt_private_key: str = _DEFAULT_PLACEHOLDER_KEY
    access_token_cookie: str = "auth_access_token"
    auth_url_prefix: str = "/auth"
    testing: bool = False
    allow_dummy_auth: bool = False

    # Crowd-specific settings
    crowd_url: Optional[str] = None
    crowd_app_name: Optional[str] = None
    crowd_app_password: Optional[str] = None

    @field_validator('des_key')
    @classmethod
    def validate_des_key(cls, v):
        if v == _DEFAULT_PLACEHOLDER_DES_KEY:
            raise ValueError('des_key must be changed from the default placeholder value')
        try:
            decoded = base64.b64decode(v)
        except Exception:
            raise ValueError('des_key is not valid base64')
        if len(decoded) != 8:
            raise ValueError(f'des_key must decode to exactly 8 bytes, got {len(decoded)}')
        return v

    @field_validator('session_salt')
    @classmethod
    def validate_session_salt(cls, v):
        if v == _DEFAULT_PLACEHOLDER_SALT:
            raise ValueError('session_salt must be changed from the default placeholder value')
        if len(v) < 16:
            raise ValueError(f'session_salt must be at least 16 characters, got {len(v)}')
        return v

    @field_validator('jwt_private_key')
    @classmethod
    def validate_jwt_private_key(cls, v):
        stripped = v.strip()
        if 'BEGIN RSA PRIVATE KEY' not in stripped and 'BEGIN PRIVATE KEY' not in stripped:
            raise ValueError('jwt_private_key must be a valid RSA private key in PEM format')
        return v

    @field_validator('auth_url_prefix')
    @classmethod
    def validate_auth_url_prefix(cls, v):
        if not v.startswith('/'):
            raise ValueError('auth_url_prefix must start with /')
        if len(v) > 1 and v.endswith('/'):
            raise ValueError('auth_url_prefix must not end with /')
        return v

    @field_validator('authenticator')
    @classmethod
    def validate_authenticator(cls, v):
        if v not in AUTHENTICATOR_MAP:
            allowed = ', '.join(sorted(AUTHENTICATOR_MAP.keys()))
            raise ValueError(f'authenticator must be one of: {allowed}')
        return v

    @field_validator('crowd_url')
    @classmethod
    def validate_crowd_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('crowd_url must start with http:// or https://')
        return v

    @model_validator(mode='after')
    def validate_authenticator_constraints(self):
        # DummyAuthenticator guard
        if self.authenticator == 'dummy' and not self.testing and not self.allow_dummy_auth:
            raise ValueError(
                "authenticator 'dummy' is not allowed in production. "
                "Set testing=true or allow_dummy_auth=true to enable it."
            )

        # Crowd fields required when using CrowdAuthenticator
        if self.authenticator == 'crowd':
            missing = []
            if not self.crowd_url:
                missing.append('crowd_url')
            if not self.crowd_app_name:
                missing.append('crowd_app_name')
            if not self.crowd_app_password:
                missing.append('crowd_app_password')
            if missing:
                raise ValueError(
                    f"authenticator 'crowd' requires: {', '.join(missing)}"
                )

        return self

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (
            kwargs.get('env_settings', None),
            TomlConfigSettingsSource(settings_cls),
            kwargs.get('init_settings', None),
        )

    def to_flask_config(self):
        """Convert to uppercase dict for Flask app.config."""
        result = {}
        for field_name in type(self).model_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name.upper()] = value
        # Add the resolved authenticator class path for get_authenticator()
        result['AUTHENTICATOR_CLASS'] = AUTHENTICATOR_MAP[self.authenticator]
        # Pre-decode the DES key from base64 to bytes for use by DES cipher
        result['DES_KEY_BYTES'] = base64.b64decode(self.des_key)
        return result


def load_config(config_path=None):
    """Load and validate configuration from a TOML file.

    Args:
        config_path: Path to TOML config file. If None, reads from
                     DAEMON_SETTINGS environment variable.

    Returns:
        Validated AppConfig instance.
    """
    toml_file = config_path or os.environ.get('DAEMON_SETTINGS', 'config.toml')

    # Dynamically create a subclass with the correct toml_file path
    DynamicConfig = type('DynamicConfig', (AppConfig,), {
        'model_config': SettingsConfigDict(toml_file=toml_file),
    })
    # Inherit the custom sources
    DynamicConfig.settings_customise_sources = AppConfig.settings_customise_sources

    return DynamicConfig()
