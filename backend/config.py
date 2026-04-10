import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""

    # Secret Key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "fallback-dev-key-change-in-production"
    )

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:Harvi%4057@localhost:5432/Frozen-Food"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development environment"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment"""
    DEBUG = False


class TestingConfig(Config):
    """Testing environment"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"