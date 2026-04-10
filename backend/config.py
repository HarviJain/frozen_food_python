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
        "postgresql+psycopg2://frozen_food_5on2_user:t1Uldo08yVYlrBNvyfYEd73Z8Ed59Rj3@dpg-d7ce209kh4rs73cjpngg-a.oregon-postgres.render.com:5432/frozen_food_5on2"
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