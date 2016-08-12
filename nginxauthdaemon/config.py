
class DefaultConfig(object):
    REALM_NAME = "Realm"
    SESSION_COOKIE = "auth_session"
    TARGET_HEADER = "X-Target"
    SESSION_SALT = "3LGFrKBEgEu4KRS40zrqw9JoyYxMKexKUQfYRf2iAb0="
    DES_IV = '\xf5\xdef\x16\xae]Y\xc6'
    DES_KEY = '\xc8\x9a\x17\x8f\x17\xd7\x93:'
    AUTHENTICATOR = 'auth.DummyAuthenticator'
