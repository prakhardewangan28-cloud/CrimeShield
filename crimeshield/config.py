"""
Configuration module for CRIMESHIELD.
Demonstrates: Module-level constants, type hints, and path management.
"""

import os
from pathlib import Path
from typing import Final

# Get the absolute path to the crimeshield directory
# This ensures database path works regardless of where the app is launched
BASE_DIR: Path = Path(__file__).resolve().parent

# Database configuration
DATABASE_NAME: Final[str] = "crimeshield.db"
DATABASE_PATH: Path = BASE_DIR / DATABASE_NAME

# Valid case statuses - using Final to indicate these shouldn't be modified
VALID_STATUSES: Final[tuple[str, ...]] = ("open", "under_review", "closed")

# Flask configuration
class Config:
    """Flask application configuration."""
    
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.environ.get('DEBUG', 'True').lower() == 'true'
    TESTING: bool = False
    
    # Database
    DATABASE_PATH: Path = DATABASE_PATH
    
    # API configuration
    JSON_SORT_KEYS: bool = False
    JSONIFY_PRETTYPRINT_REGULAR: bool = True


class TestConfig(Config):
    """Test configuration - uses separate database."""
    
    TESTING: bool = True
    DATABASE_PATH: Path = BASE_DIR / "test_crimeshield.db"
