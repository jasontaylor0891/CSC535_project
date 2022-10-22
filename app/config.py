import os


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY')

    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB')
    MYSQL_CURSORCLASS = os.environ.get('MYSQL_CURSORCLASS')
    
class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = os.environ.get('DEV_MYSQL_HOST')
    MYSQL_USER = os.environ.get('DEV_MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('DEV_MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('DEV_MYSQL_DB')
    MYSQL_CURSORCLASS = os.environ.get('DEV_MYSQL_CURSORCLASS')

class TestingConfig(Config):
    TESTING = True
    MYSQL_HOST = os.environ.get('TEST_MYSQL_HOST')
    MYSQL_USER = os.environ.get('TEST_MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('TEST_MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('TEST_MYSQL_DB')
    MYSQL_CURSORCLASS = os.environ.get('TEST_MYSQL_CURSORCLASS')

class ProductionConfig(Config):
   pass
