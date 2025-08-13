"""
Production configuration for Google Cloud deployment
"""

import os
import logging

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Flask settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = False
    TESTING = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = '/tmp'  # Use /tmp in Cloud Run
    
    # Firebase settings
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '/app/serviceAccount.json')
    
    # Logging
    LOG_LEVEL = logging.INFO

class ProductionConfig(Config):
    """Production configuration for Google Cloud"""
    DEBUG = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Development settings
    SESSION_COOKIE_SECURE = False

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    return config.get(env, config['default'])
