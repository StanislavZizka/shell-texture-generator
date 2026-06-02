"""
Page Routes - HTML Template Rendering

In the original November prototype, all routes were mixed together in app.py.
Now we're separating concerns properly - this file only handles pages that
show HTML to users (not API endpoints that return data).

This follows Flask Blueprint pattern for better code organization.
"""
from pathlib import Path

from flask import Blueprint, render_template, send_from_directory
from config import STATIC_MODE_PRESETS
from config_211 import (
    FIG211_DEFAULT_DEVELOPMENT,
    FIG211_DEVELOPMENT_ORDER,
    FIG211_DEVELOPMENT_PRESETS,
    FIG211_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    MODEL_211_PARAMS,
    SPOTS_211_PRESETS,
    SPOTS_211_RANDOM_ERROR_PRESETS,
)
from config_23 import (
    FIG23_DEFAULT_DEVELOPMENT,
    FIG23_DEFAULT_STAGE,
    FIG23_DEVELOPMENT_ORDER,
    FIG23_DEVELOPMENT_PRESETS,
    FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    FIG23_MODEL_PARAMS,
    FIG23_PROGRESSION_LEVELS,
    FIG23_PROGRESSION_ORDER,
    FIG23_STRIPE_VARIANTS,
    FIG23_STAGE_ORDER,
    FIG23_STAGE_PRESETS,
)
from config_212 import (
    FIG212_DEFAULT_DEVELOPMENT,
    FIG212_DEVELOPMENT_ORDER,
    FIG212_DEVELOPMENT_PRESETS,
    FIG212_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    FIG212_DEFAULT_STAGE,
    MODEL_212_PARAMS,
    FIG212_STAGE_ORDER,
    FIG212_STAGE_PRESETS,
    RANDOM_ERROR_212_STAGES,
)

# Create a Blueprint - think of it as a mini-app for organizing related routes
# The 'pages' name helps Flask organize our URL routing
pages = Blueprint('pages', __name__)
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'

FIG211_OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'search_results' / '211' / 'meinhardt_clean_sampling_v4'

FIG211_PARAMETER_KEYS = [
    'K',
    't_max',
    'dt',
    'size',
    's',
    'r_a',
    'r_b',
    'b_a',
    'b_b',
    'D_a',
    'D_b',
    'seed',
]

FIG212_PARAMETER_KEYS = [
    's',
    'r_a',
    'r_b',
    'b_a',
    'b_b',
    'D_a',
    'D_b',
    'K',
    'delta_t',
    'dx',
    'random_seed',
    'initial_noise_a_amplitude',
    'initial_noise_b_amplitude',
    'initial_noise_smoothing_passes',
    'early_smoothing_fraction',
    'early_smoothing_strength',
]

FIG23_PARAMETER_KEYS = [
    's',
    'r_a',
    'r_b',
    'b_a',
    'b_b',
    'D_a',
    'D_b',
    'K',
    'delta_t',
    'dx',
    'random_seed',
    'initial_noise_a_amplitude',
    'initial_noise_b_amplitude',
]

# ---------------------------------------------------------------------------
# AKTUÁLNĚ AKTIVNÍ UI PLOCHA
# Tyto stránky teď používám nejvíc a kolem nich průběžně uklízím templates/CSS:
# - /
# - /spots_211
# - /figure_23
# - /activator_212
# Když refaktoruji frontend, beru tyto routy jako hlavní prioritu.
# ---------------------------------------------------------------------------

@pages.route('/')
def home():
    """
    Main homepage route.
    
    When users visit the website root (like http://localhost:5000/), 
    they get the home.html template rendered with all the CSS and content.
    
    Returns:
        Rendered HTML template for the homepage
    """
    return render_template('home.html')

# ---------------------------------------------------------------------------
# VEDLEJŠÍ / STARŠÍ SAMOSTATNÉ STRÁNKY
# Tyto routy v projektu nechávám, ale momentálně nejsou hlavní pracovní plocha
# pro refactor aktivních figure pages výše.
# ---------------------------------------------------------------------------

@pages.route('/activator_inhibitor')
def activator_inhibitor():
    """
    Activator-Inhibitor model page route.

    Renders the texture generation interface for reaction-diffusion
    mathematical models. Users can adjust parameters and generate patterns.

    Returns:
        Rendered HTML template for the activator-inhibitor interface
    """
    # Pass presets to the template for dynamic UI updates
    return render_template('activator_inhibitor.html', presets=STATIC_MODE_PRESETS)

@pages.route('/random_error')
def random_error():
    """
    Random Error model page route.

    Renders the texture generation interface with biological noise injection.
    Simulates imperfections in shell patterns from initialization or growth.

    Returns:
        Rendered HTML template for the random error interface
    """
    return render_template('random_error.html')

@pages.route('/localized_disturbance')
def localized_disturbance():
    """
    Localized Disturbance model page route.

    Renders the interface for localized pattern stability breakdown.
    Simulates biological pigment defects from chapter 1.8 of Algorithmic Beauty.

    Returns:
        Rendered HTML template for the localized disturbance interface
    """
    return render_template('localized_disturbance.html')

@pages.route('/oscillatory_waves')
def oscillatory_waves():
    """
    Oscillatory Waves model page route.

    Renders the analytical solution interface for Riccati ODE.
    Follows exact mathematical derivation from vypocet.txt (SOURCE OF TRUTH).

    This is a pure mathematical model demonstrating:
    - Riccati differential equation: da/dt = k·a² - r_a·a + b_a
    - Analytical solution via partial fraction decomposition
    - Equilibrium point analysis (discriminant method)
    - Asymptotic behavior and saturation dynamics

    Returns:
        Rendered HTML template for the oscillatory waves interface
    """
    return render_template('oscillatory_waves.html')


# ---------------------------------------------------------------------------
# AKTIVNÍ FIGURE PAGES
# /spots_211 a /activator_212 záměrně sdílí stejný template `figure_211_212.html`
# a rozlišují se přes `figure_mode`.
# /figure_23 má vlastní sesterský template `activator_23.html`.
# ---------------------------------------------------------------------------

@pages.route('/activator_212')
def activator_212():
    """
    Figure 2.12 activator-inhibitor page route.

    Note:
        This route intentionally uses the shared figure template
        `figure_211_212.html` with `figure_mode='212'`.

    Returns:
        Rendered HTML template for stage-based labyrinth generation.
    """
    return render_template(
        'figure_211_212.html',
        figure_mode='212',
        api_endpoint='/api/generate-212',
        page_title='Figure 2.12 - Labyrinths',
        page_header='Figure 2.12 - Labyrinths',
        page_subtitle='Stage and development views of labyrinth evolution',
        nav_label='Figure 2.12 - Labyrinths',
        stages=FIG212_STAGE_PRESETS,
        stage_order=FIG212_STAGE_ORDER,
        default_stage=FIG212_DEFAULT_STAGE,
        development_presets=FIG212_DEVELOPMENT_PRESETS,
        development_order=FIG212_DEVELOPMENT_ORDER,
        default_development=FIG212_DEFAULT_DEVELOPMENT,
        development_random_error_presets=FIG212_DEVELOPMENT_RANDOM_ERROR_PRESETS,
        random_error_presets=RANDOM_ERROR_212_STAGES,
        model_params=MODEL_212_PARAMS,
        parameter_keys=FIG212_PARAMETER_KEYS,
    )


@pages.route('/figure_23')
def figure_23():
    """
    Figure 2.3 stripe preset page.

    Renders the stripe-focused activator-inhibitor interface using a small
    local parameter sweep around the current best stripe preset.
    """
    return render_template(
        'activator_23.html',
        figure_mode='23',
        api_endpoint='/api/generate-23',
        page_title='Figure 2.3 - Stripes',
        page_header='Figure 2.3 - Stripes',
        page_subtitle='Dominant, well-separated vertical stripe bands',
        nav_label='Figure 2.3 - Stripes',
        stages=FIG23_STAGE_PRESETS,
        stage_order=FIG23_STAGE_ORDER,
        default_stage=FIG23_DEFAULT_STAGE,
        development_presets=FIG23_DEVELOPMENT_PRESETS,
        development_order=FIG23_DEVELOPMENT_ORDER,
        default_development=FIG23_DEFAULT_DEVELOPMENT,
        development_random_error_presets=FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS,
        progression_order=FIG23_PROGRESSION_ORDER,
        progression_levels=FIG23_PROGRESSION_LEVELS,
        stripe_variants=FIG23_STRIPE_VARIANTS,
        model_params=FIG23_MODEL_PARAMS,
        parameter_keys=FIG23_PARAMETER_KEYS,
    )

@pages.route('/spots_211')
def spots_211():
    """
    Figure 2.11 spot-pattern reference page.

    Note:
        This route intentionally reuses `figure_211_212.html` with
        `figure_mode='211'` so the active figure pages keep the same UI shell.

    Renders the current best Figure 2.11 output and its developmental strip.
    """
    return render_template(
        'figure_211_212.html',
        figure_mode='211',
        api_endpoint='/api/generate-211',
        page_title='Figure 2.11 - Spots',
        page_header='Figure 2.11 - Spots',
        page_subtitle='Meinhardt spot evolution from Figure 2.11',
        nav_label='Figure 2.11 - Spots',
        stages=SPOTS_211_PRESETS,
        stage_order=['stage_1', 'stage_2', 'stage_3', 'stage_4'],
        default_stage='stage_3',
        development_presets=FIG211_DEVELOPMENT_PRESETS,
        development_order=FIG211_DEVELOPMENT_ORDER,
        default_development=FIG211_DEFAULT_DEVELOPMENT,
        development_random_error_presets=FIG211_DEVELOPMENT_RANDOM_ERROR_PRESETS,
        random_error_presets=SPOTS_211_RANDOM_ERROR_PRESETS,
        model_params=MODEL_211_PARAMS['params'],
        model_bundle=MODEL_211_PARAMS,
        parameter_keys=FIG211_PARAMETER_KEYS,
    )

@pages.route('/spots_211/assets/<path:filename>')
def spots_211_assets(filename):
    """
    Serve the latest Figure 2.11 reference outputs from the search_results folder.
    """
    return send_from_directory(FIG211_OUTPUT_DIR, filename)

@pages.route('/assets/<path:filename>')
def assets(filename):
    """
    Serve static assets (3D models, textures, etc.).
    
    Provides access to 3D shell models and other resource files
    needed for the visualization components.
    
    Args:
        filename: Path to the asset file within the assets directory
        
    Returns:
        File response for the requested asset
    """
    return send_from_directory(ASSETS_DIR, filename)
