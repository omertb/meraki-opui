class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = 'YOUR_SECRET_KEY'
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://USER:PASS@localhost/DATABASE_NAME"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False