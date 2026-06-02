"""Centralized filesystem paths for the project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "configs"
PRESETS_DIR = CONFIG_DIR / "presets"

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUTS_DIR = BASE_DIR / "outputs"

EXPERIMENTS_DIR = BASE_DIR / "experiments"
RUNS_DIR = EXPERIMENTS_DIR / "runs"
REPORTS_DIR = EXPERIMENTS_DIR / "reports"
REFERENCES_DIR = EXPERIMENTS_DIR / "references"

