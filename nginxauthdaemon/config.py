
class DefaultConfig(object):
    REALM_NAME = "Realm"
    SESSION_COOKIE = "auth_session"
    TARGET_HEADER = "X-Target"
    SESSION_SALT = "3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="
    DES_KEY = '\xc8\x9a\x17\x8f\x17\xd7\x93:'
    AUTHENTICATOR = 'nginxauthdaemon.auth.DummyAuthenticator'
    JWT_PRIVATE_KEY = """
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
    ACCESS_TOKEN_COOKIE = "auth_access_token"
