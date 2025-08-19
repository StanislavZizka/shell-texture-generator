"""
Configuration Settings for Shell Texture Generator

After working with the prototype version from November 2024, we learned that
proper configuration management is crucial. This file centralizes all settings
so they're easy to modify without digging through code.

This approach follows modern Flask best practices for maintainable applications.
"""
import os
from pathlib import Path

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent

# Directory paths - organized like a professional web application
STATIC_DIR = BASE_DIR / "static"          # CSS, JS, images for the website
TEMPLATES_DIR = BASE_DIR / "templates"    # HTML template files
ASSETS_DIR = BASE_DIR / "assets"          # 3D models and other resources

# Image generation settings
IMAGES_DIR = STATIC_DIR / "images"        # Where generated textures are saved
DEFAULT_TEXTURE_SIZE = 512                # Default image size (512x512 pixels)
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg']  # File types we can save

# Default values for texture generation
# These came from experimentation in the original November prototype
TEXTURE_DEFAULTS = {
    'K': 1.0,                 # Scaling factor for the mathematical model
    't_max': 10.0,            # How long to run the simulation
    'delta_t': 0.1,           # Time step size (smaller = more precise)
    'color1': '#0000ff',      # Primary color (blue)
    'color2': '#ff0000'       # Secondary color (red)
}

# Advanced mathematical parameters for the reaction-diffusion system
# These control how the shell patterns form and spread
SIMULATION_PARAMS = {
    'D_a': 0.02,              # How fast activator molecules spread
    'D_b': 0.1,               # How fast inhibitor molecules spread (5x faster)
    'feed_rate': 0.035,       # Rate of activator production
    'kill_rate': 0.06,        # Rate of inhibitor removal
    'random_seed': 42         # For reproducible results during development
}

# Flask application configuration classes
# Different settings for development, testing, and production deployment
class Config:
    """
    Base configuration that other environments inherit from.
    Contains settings common to all deployment types.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-testing-only'
    DEBUG = False             # Don't show detailed errors to users by default
    TESTING = False

class DevelopmentConfig(Config):
    """
    Settings for local development.
    Enables debug mode for easier troubleshooting.
    """
    DEBUG = True              # Show detailed error pages during development

class ProductionConfig(Config):
    """
    Settings for live deployment.
    Prioritizes security and performance over debugging convenience.
    """
    DEBUG = False             # Never show internal errors to real users

class TestingConfig(Config):
    """
    Settings for automated testing.
    """
    TESTING = True
    DEBUG = True

# Easy way to select configuration based on environment
# Usage: config['development'] or config['production']
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig, 
    'testing': TestingConfig,
    'default': DevelopmentConfig     # Use development settings if nothing specified
}