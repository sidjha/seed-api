import os

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True 