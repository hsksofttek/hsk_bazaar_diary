import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DB = os.path.join(BASEDIR, 'instance', 'business_web.db')

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration - SQLite"""
    DEBUG = True
    # Use instance database where sample data is stored
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + INSTANCE_DB

class ProductionConfig(Config):
    """Production configuration - PostgreSQL"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/business_web'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 
 
 
 