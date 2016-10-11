import os

DATABASE_URL=os.environ.get('DATABASE_URL')

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class ProdConfig(Config):
    DEVELOPMENT = False
    DEBUG = False