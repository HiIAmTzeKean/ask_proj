import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "this_is_trial_run"
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=10)
    SESSION_REFRESH_EACH_REQUEST = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = mysql://HiIAmTzeKean:pppppppp@server/db
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TESTING = True