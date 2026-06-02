"""Figure 2.11 reference configuration loaded from versioned JSON."""

from __future__ import annotations

from pathlib import Path

from core.presets import load_figure_211_presets

BASE_DIR = Path(__file__).resolve().parent
_FIG211_BUNDLE = load_figure_211_presets()

FIG211_REFERENCE_DIR = BASE_DIR / _FIG211_BUNDLE["figure_211_reference_dir"]
MODEL_211_PARAMS = dict(_FIG211_BUNDLE["model_211_params"])
SPOTS_211_PRESETS = dict(_FIG211_BUNDLE["spots_presets"])
SPOTS_211_RANDOM_ERROR_PRESETS = dict(_FIG211_BUNDLE["random_error_presets"])
FIG211_DEVELOPMENT_ORDER = list(_FIG211_BUNDLE["development_order"])
FIG211_DEFAULT_DEVELOPMENT = str(_FIG211_BUNDLE["default_development"])
FIG211_DEVELOPMENT_PRESETS = dict(_FIG211_BUNDLE["development_presets"])
FIG211_DEVELOPMENT_RANDOM_ERROR_PRESETS = dict(_FIG211_BUNDLE["development_random_error_presets"])
