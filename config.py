# default config
import os


class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ['FSECRETKEY']
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://{}@my-postgres/meraki_operator".format(os.environ['PGCRED'])
    SECURITY_PASSWORD_SALT = os.environ['PASSWDSALT']
    # Google ReCaptcha Keys:
    RECAPTCHA_PUBLIC_KEY = os.environ['CAPTCHAPUBKEY']
    RECAPTCHA_PRIVATE_KEY = os.environ['CAPTCHAPRIKEY']


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DevelopmentConfig(BaseConfig):
    SESSION_COOKIE_SECURE = False
    RECAPTCHA_USE_SSL = False
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    # Google ReCaptcha
    RECAPTCHA_USE_SSL = True
    # session headers
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True