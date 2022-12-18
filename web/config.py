import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    MONGODB_SETTINGS = {
        'db': 'blog-nodv',
        'host': 'mongodb+srv://nodv:nodv@blog-nodv.vbgx2gc.mongodb.net/?retryWrites=true&w=majority'
    }
    SECRET_KEY = os.environ.get("SECRET_KEY", "framgia123")


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
