"""Tests for Pydantic configuration validation."""
import os
import pytest
from pydantic import ValidationError

from nginxauthdaemon.config import AppConfig, load_config, _DEFAULT_PLACEHOLDER_SALT


_test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.toml')


def _make_config(**overrides):
    """Create an AppConfig with test defaults, overriding specified fields."""
    defaults = {
        'realm_name': 'Test',
        'session_salt': 'test-salt-value-long-enough-for-validation',
        'des_key': '\xc8\x9a\x17\x8f\x17\xd7\x93:',
        'authenticator': 'dummy',
        'testing': True,
        'auth_url_prefix': '/auth',
        'jwt_private_key': """
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
""",
    }
    defaults.update(overrides)
    return AppConfig(**defaults)


# --- US-001: Validated Configuration at Startup ---

class TestDesKeyValidation:
    def test_valid_des_key_accepted(self):
        config = _make_config(des_key='\xc8\x9a\x17\x8f\x17\xd7\x93:')
        assert len(config.des_key.encode('raw_unicode_escape')) == 8

    def test_des_key_wrong_length_rejected(self):
        with pytest.raises(ValidationError, match='des_key must be exactly 8 bytes'):
            _make_config(des_key='short')

    def test_des_key_too_long_rejected(self):
        with pytest.raises(ValidationError, match='des_key must be exactly 8 bytes'):
            _make_config(des_key='toolongkey1234567')


class TestSessionSaltValidation:
    def test_valid_salt_accepted(self):
        config = _make_config(session_salt='a-valid-salt-long-enough')
        assert config.session_salt == 'a-valid-salt-long-enough'

    def test_default_placeholder_salt_rejected(self):
        with pytest.raises(ValidationError, match='session_salt must be changed from the default'):
            _make_config(session_salt=_DEFAULT_PLACEHOLDER_SALT)

    def test_short_salt_rejected(self):
        with pytest.raises(ValidationError, match='session_salt must be at least 16 characters'):
            _make_config(session_salt='short')


class TestJwtPrivateKeyValidation:
    def test_valid_rsa_key_accepted(self):
        config = _make_config()
        assert 'BEGIN RSA PRIVATE KEY' in config.jwt_private_key

    def test_malformed_key_rejected(self):
        with pytest.raises(ValidationError, match='jwt_private_key must be a valid RSA private key'):
            _make_config(jwt_private_key='not-a-key')

    def test_empty_key_rejected(self):
        with pytest.raises(ValidationError, match='jwt_private_key must be a valid RSA private key'):
            _make_config(jwt_private_key='')


class TestAuthUrlPrefixValidation:
    def test_valid_prefix_accepted(self):
        config = _make_config(auth_url_prefix='/auth')
        assert config.auth_url_prefix == '/auth'

    def test_prefix_without_slash_rejected(self):
        with pytest.raises(ValidationError, match='auth_url_prefix must start with /'):
            _make_config(auth_url_prefix='auth')

    def test_trailing_slash_rejected(self):
        with pytest.raises(ValidationError, match='auth_url_prefix must not end with /'):
            _make_config(auth_url_prefix='/auth/')

    def test_root_slash_accepted(self):
        config = _make_config(auth_url_prefix='/')
        assert config.auth_url_prefix == '/'


class TestAuthenticatorEnumValidation:
    def test_crowd_accepted(self):
        config = _make_config(
            authenticator='crowd',
            crowd_url='http://crowd.example.com/',
            crowd_app_name='app',
            crowd_app_password='pass',
        )
        assert config.authenticator == 'crowd'

    def test_dummy_accepted_with_testing(self):
        config = _make_config(authenticator='dummy', testing=True)
        assert config.authenticator == 'dummy'

    def test_invalid_authenticator_rejected(self):
        with pytest.raises(ValidationError, match='authenticator must be one of'):
            _make_config(authenticator='ldap')


class TestStartupErrorFormatting:
    def test_create_app_exits_on_invalid_config(self, tmp_path):
        """create_app() exits with code 1 on invalid config."""
        bad_config = tmp_path / 'bad.toml'
        bad_config.write_text('session_salt = "short"\n')

        from nginxauthdaemon.nginxauthdaemon import create_app
        with pytest.raises(SystemExit) as exc_info:
            create_app(str(bad_config))
        assert exc_info.value.code == 1

    def test_load_config_from_toml_file(self):
        """load_config successfully loads from a TOML file."""
        config = load_config(_test_config_path)
        assert config.authenticator == 'dummy'
        assert config.testing is True
        assert config.auth_url_prefix == '/auth'


# --- US-002: Remove DummyAuthenticator from Production ---

class TestDummyAuthenticatorBlocking:
    def test_dummy_rejected_in_production(self):
        with pytest.raises(ValidationError, match="authenticator 'dummy' is not allowed in production"):
            _make_config(authenticator='dummy', testing=False, allow_dummy_auth=False)

    def test_dummy_allowed_with_testing_true(self):
        config = _make_config(authenticator='dummy', testing=True)
        assert config.authenticator == 'dummy'

    def test_dummy_allowed_with_allow_dummy_auth_true(self):
        config = _make_config(authenticator='dummy', testing=False, allow_dummy_auth=True)
        assert config.authenticator == 'dummy'

    def test_crowd_always_allowed(self):
        config = _make_config(
            authenticator='crowd',
            testing=False,
            crowd_url='http://crowd.example.com/',
            crowd_app_name='app',
            crowd_app_password='pass',
        )
        assert config.authenticator == 'crowd'


# --- US-003: Crowd-Specific Config Validation ---

class TestCrowdConfigValidation:
    def test_crowd_missing_all_fields_rejected(self):
        with pytest.raises(ValidationError, match="authenticator 'crowd' requires"):
            _make_config(authenticator='crowd')

    def test_crowd_missing_url_rejected(self):
        with pytest.raises(ValidationError, match='crowd_url'):
            _make_config(
                authenticator='crowd',
                crowd_app_name='app',
                crowd_app_password='pass',
            )

    def test_crowd_missing_app_name_rejected(self):
        with pytest.raises(ValidationError, match='crowd_app_name'):
            _make_config(
                authenticator='crowd',
                crowd_url='http://crowd.example.com/',
                crowd_app_password='pass',
            )

    def test_crowd_missing_password_rejected(self):
        with pytest.raises(ValidationError, match='crowd_app_password'):
            _make_config(
                authenticator='crowd',
                crowd_url='http://crowd.example.com/',
                crowd_app_name='app',
            )

    def test_crowd_invalid_url_rejected(self):
        with pytest.raises(ValidationError, match='crowd_url must start with http'):
            _make_config(
                authenticator='crowd',
                crowd_url='ftp://crowd.example.com/',
                crowd_app_name='app',
                crowd_app_password='pass',
            )

    def test_crowd_fields_ignored_when_dummy(self):
        """Crowd fields are not required when authenticator is dummy."""
        config = _make_config(authenticator='dummy', testing=True)
        assert config.crowd_url is None

    def test_crowd_valid_config_accepted(self):
        config = _make_config(
            authenticator='crowd',
            crowd_url='https://crowd.example.com/crowd/',
            crowd_app_name='testapp',
            crowd_app_password='testpass',
        )
        assert config.crowd_url == 'https://crowd.example.com/crowd/'


# --- US-004: Pydantic-Based Config Model ---

class TestFlaskConfigPopulation:
    def test_all_fields_accessible_on_flask_config(self):
        """All AppConfig fields are available in Flask config with uppercase keys."""
        from nginxauthdaemon.nginxauthdaemon import create_app
        app = create_app(_test_config_path)

        assert app.config['REALM_NAME'] == 'Realm'
        assert app.config['SESSION_COOKIE'] == 'auth_session'
        assert app.config['TARGET_HEADER'] == 'X-Target'
        assert app.config['AUTH_URL_PREFIX'] == '/auth'
        assert app.config['AUTHENTICATOR'] == 'dummy'
        assert app.config['AUTHENTICATOR_CLASS'] == 'nginxauthdaemon.auth.DummyAuthenticator'
        assert app.config['TESTING'] is True
        assert len(app.config['DES_KEY'].encode('raw_unicode_escape')) == 8


# --- US-005: Env var override ---

class TestEnvVarOverride:
    def test_env_var_overrides_toml_value(self, tmp_path, monkeypatch):
        """Environment variables take precedence over TOML file values."""
        config_file = tmp_path / 'test.toml'
        config_file.write_text(
            'realm_name = "FromFile"\n'
            'authenticator = "dummy"\n'
            'testing = true\n'
            'session_salt = "test-salt-from-file-long-enough"\n'
            'des_key = "\\u00c8\\u009a\\u0017\\u008f\\u0017\\u00d7\\u0093:"\n'
            'jwt_private_key = """\n'
            '-----BEGIN RSA PRIVATE KEY-----\n'
            'MIICXAIBAAKBgQCwvaYt11Xpp3CaEtSfyMQrKGMbmPBUJ0vs8vQk1ukkkaSbYOQt\n'
            'Sii9hQrUjz4BJjHhxgc0lZHLPnbSdU0j5f12Ug/dNxSQ+gj015K6DtZp9Ltcoa5h\n'
            'BbHb2+C9elCha9Kp8QpLH7PYz8L/Z2/YRlgodT1aqgczrsc0vH/EVzKCjQIDAQAB\n'
            'AoGBAKX48t2JonxRaUTG+jUy7EU7IBcCgG4GmR5i6TLPPxHAU7w2ORDu22NeVNVX\n'
            'zvp1S9KhjJKtAsTCXAM3dMGJcYLjPWUp9owrLKoevzH4mmsv2/4cDRKh79Img3MQ\n'
            'eIk570oe9jJg3C9MmPXbR/B8EB1G+97M6FnWJrzb4fU1JClhAkEA4hVzFW4dvLmW\n'
            '1CtcPIhJsx9fvCeFyoQAs4b4FWmqY7BYkSRVLfeSllI2YvUq58Ufda7/njbUa1Ki\n'
            'OHfnK/MMDwJBAMggtviBHwIbVVBVsYOWOLSVtPwbz0nxpBdSpKqixfif9Hj0XTTt\n'
            'fYcKnVcmAT5+KjZkTX/JsEyaqXdKYVDP26MCQHRi6m3b1D81o2nyMHeRCa/GtPgd\n'
            'uIh60Ambr9cGIItVWyLM+3TAgJwWEp167O2H0xw4TKtcOppNXemIAF/lrQ0CQFaB\n'
            'DZXM+kJG3lGjON/QByLHsztmKeukb3FFX7gCM+CMA3hk6AUAwsmkZO5OlysUDdsE\n'
            '8BrUa0gxch8GH5p2vlECQAmlBjmwbYOJ9lXWppKlUDbtk9DFm40YRB83ysZMZoUZ\n'
            'C4cnTxWQ/CrQSwiSHy5Xr13jVLhVgmtudfJsfzUgxw8=\n'
            '-----END RSA PRIVATE KEY-----\n'
            '"""\n'
        )

        monkeypatch.setenv('REALM_NAME', 'FromEnvVar')
        config = load_config(str(config_file))
        assert config.realm_name == 'FromEnvVar'
