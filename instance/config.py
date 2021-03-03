import os
from datetime import timedelta


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    SESSION_REFRESH_EACH_REQUEST = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TESTING = True