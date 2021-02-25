import os
from datetime import timedelta


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "this_is_trial_run"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    SESSION_REFRESH_EACH_REQUEST = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = 'postgres://koxidiekcuiyij:7de5f27ee76ab74bb988079f5a58a05e2d1aadf29ef9afe86da374197e020201@ec2-52-20-66-171.compute-1.amazonaws.com:5432/ddkphlrmcldua2'
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEBUG = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TESTING = True