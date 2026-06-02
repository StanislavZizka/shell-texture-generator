"""Core domain models, validation, presets, and shared project paths."""

from .models import EvaluationResult, ExperimentRecord, SimulationParams, SimulationOutput
from .paths import (
    ASSETS_DIR,
    BASE_DIR,
    CONFIG_DIR,
    EXPERIMENTS_DIR,
    OUTPUTS_DIR,
    PRESETS_DIR,
    REFERENCES_DIR,
    REPORTS_DIR,
    RUNS_DIR,
    STATIC_DIR,
    TEMPLATES_DIR,
)
from .presets import (
    load_activator_inhibitor_presets,
    load_figure_211_presets,
    load_figure_212_presets,
    load_figure_23_presets,
    load_preset_bundle,
)
from .modes import ModeDefinition, get_mode_definition, load_mode_registry
from .modes_result import ModeGenerationResult
from .validation import ValidationError, validate_simulation_params
