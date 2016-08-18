import os

DATABASE_URL="postgresql://localhost/seed_db_dev"

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True 