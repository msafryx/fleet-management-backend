import os
from datetime import timedelta
import dotenv

dotenv.load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5433/maintenance_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JSON_SORT_KEYS = False
    
    # Pagination
    ITEMS_PER_PAGE = 10
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # OIDC / Keycloak
    OIDC_ISSUER = os.environ.get('OIDC_ISSUER')  # e.g. http://keycloak:8080/realms/fleet-management-app
    AUTH_DISABLED = os.environ.get('AUTH_DISABLED', 'False').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Allow all origins in development
    CORS_ORIGINS = ['*']

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
