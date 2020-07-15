"""
Configuration settings for the application
"""
import os
import datetime

listen_addr = os.getenv('LISTEN_ADDR', '127.0.0.1')
listen_port = os.getenv('LISTEN_PORT', 7777)

class Config(object):
    # Flask settings
    SERVER_HOST = listen_addr
    SERVER_PORT = listen_port

    SQLALCHEMY_DATABASE_URI = 'sqlite:///tzkeeper.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False
    RESTPLUS_ERROR_INCLUDE_MESSAGE = False

    JWT_SECRET_KEY = 'You_Will_Never_guess_This_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)

    TIMEZONE_INITIAL_VALUES = "IANA_timezone_names.json"
    DEBUG = False
    FLASK_DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    DEBUG = False
    FLASK_DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://' #in memory db
