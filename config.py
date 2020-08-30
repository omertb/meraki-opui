# default config
import os


class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ['FSECRETKEY']
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://{}@opui-postgres/meraki_operator".format(os.environ['PGCRED'])
    SECURITY_PASSWORD_SALT = os.environ['PASSWDSALT']


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False