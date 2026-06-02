"""Application configuration and legacy compatibility settings."""

from __future__ import annotations

import os
from pathlib import Path

from core.presets import load_activator_inhibitor_presets

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = STATIC_DIR / "images"

DEFAULT_TEXTURE_SIZE = 512
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg"]

TEXTURE_DEFAULTS = {
    "K": 1.0,
    "t_max": 400.0,
    "delta_t": 0.1,
    "color1": "#0000ff",
    "color2": "#ff0000",
}

SIMULATION_PARAMS = {
    "s": 0.050028,
    "r_a": 0.342588,
    "r_b": 0.750365,
    "b_a": 0.01,
    "b_b": 0.01,
    "D_a": 0.007425,
    "D_b": 0.977633,
    "K": 0.4408,
    "t_max": 804.0,
    "B0": 1.0,
    "dx": 1.0,
    "random_seed": 42,
}

STATIC_MODE_PRESETS = load_activator_inhibitor_presets()
SIMULATION_PRESETS = STATIC_MODE_PRESETS
PRESETS = STATIC_MODE_PRESETS


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-for-testing-only"
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

