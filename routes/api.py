"""
API Routes - JSON endpoint handlers for texture generation

Handles all AJAX requests and returns JSON responses for the texture generator.
Provides endpoints for mathematical pattern generation algorithms.
"""
import os
import glob
import time
import hashlib

from flask import Blueprint, request, jsonify, url_for
import numpy as np
from PIL import Image
from services.texture_generator import TextureGeneratorService
from services.random_error_module import create_random_error_params, run_random_error_disturbance
from config import SIMULATION_PARAMS
from config import IMAGES_DIR
from config import STATIC_DIR
from config import DEFAULT_TEXTURE_SIZE
from config_23 import (
    FIG23_DEFAULT_STAGE,
    FIG23_DEVELOPMENT_PRESETS,
    FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    FIG23_PROGRESSION_LEVELS,
    FIG23_STRIPE_VARIANTS,
    FIG23_STAGE_PRESETS,
)
from rendering.stripe_export import save_stripe_space_time_image
from routes.api_fig211_helpers import (
    apply_fig211_random_error as _apply_fig211_random_error,
    colorize_fig211_stage as _colorize_fig211_stage,
)
try:
    from config import SIMULATION_PRESETS
except Exception:
    SIMULATION_PRESETS = {}
from utils.helpers import validate_texture_params

api = Blueprint('api', __name__)

texture_service = TextureGeneratorService()

@api.route('/set_preset', methods=['POST'])
def set_preset():
    """
    Update global SIMULATION_PARAMS with a named preset.

    Expected JSON payload: { "preset": "stable|balanced|active|chaotic" }
    Returns: { "ok": true, "applied": preset_name } or { "error": ... }
    """
    try:
        data = request.get_json() or {}
        name = (data.get('preset') or '').strip().lower()
        if not name:
            return jsonify({'error': 'Missing preset name'}), 400
        if name not in SIMULATION_PRESETS:
            return jsonify({'error': f'Unknown preset: {name}'}), 400
        SIMULATION_PARAMS.update(SIMULATION_PRESETS[name])
        return jsonify({'ok': True, 'applied': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/calculate', methods=['POST'])
def calculate():
    """
    Generate mathematical texture based on reaction-diffusion parameters.

    Expected JSON payload:
    {
        "K": float,                    # Reaction constant (0.1 - 5.0)
        "t_max": float,                # Maximum simulation time
        "delta_t": float,              # Time step size
        "color1": string,              # Base color (hex format)
        "color2": string,              # Contrast color (hex format)
        "preset": string,              # Optional: stable|balanced|active|chaotic
        "enable_noise": bool,          # Optional: Enable Dynamic Instability
        "noise_target": string,        # Optional: A|B|Both
        "noise_strength": float,       # Optional: 0.001-0.05
        "enable_random_error": bool,   # Optional: Enable Biological Perturbation
        "re_strength": float,          # Optional: 0.01-0.08 (perturbation amplitude)
        "re_duration": int,            # Optional: 10-50 (steps)
        "re_frequency": float,         # Optional: 0.05-0.2 (temporal oscillation)
        "re_probability": float,       # Optional: 0.01-0.1 (trigger chance)
        "re_num_regions": int,         # Optional: 1-10 (number of zones)
        "re_region_size": int,         # Optional: 5-20 (zone size in pixels)
        "re_jitter": float,            # Optional: 0.10-0.15 (edge irregularity)
        "re_micro_noise": float,       # Optional: 0.05-0.07 (microstructure noise)
        "re_alpha_var": float          # Optional: 0.20-0.25 (amplitude variation)
    }

    Returns:
    {
        "image_url": string  # URL to generated texture image
    } or {"error": string}
    """
    try:
        # Extract and validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate mathematical parameters using helper function
        validation_result = validate_texture_params(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['error']}), 400
        
        params = validation_result['params']

        # Handle preset selection (optional) - supports both old and new Static Mode presets
        preset_key = (data.get('preset') or '').strip().lower()
        preset_params = SIMULATION_PRESETS.get(preset_key, {})

        # Dynamic Mode: Handle custom parameters (if provided)
        # Frontend sends custom_s, custom_D_b, custom_r_a, custom_r_b in Dynamic Mode
        if data.get('custom_s') is not None:
            preset_params = {
                's': float(data.get('custom_s', 0.11)),
                'D_b': float(data.get('custom_D_b', 0.35)),
                'r_a': float(data.get('custom_r_a', 0.10)),
                'r_b': float(data.get('custom_r_b', 0.18)),
            }

        # Check if Dynamic Instability mode is enabled
        enable_noise = data.get('enable_noise', False)

        # Extract noise parameters (if enabled)
        noise_target = data.get('noise_target', 'Both')
        noise_strength = float(data.get('noise_strength', 0.01))

        if enable_noise:
            # Validate noise parameters for dynamic instability mode
            if noise_target not in ['A', 'B', 'Both']:
                return jsonify({'error': 'noise_target must be A, B, or Both'}), 400
            if not (0.001 <= noise_strength <= 0.05):
                return jsonify({'error': 'noise_strength must be between 0.001 and 0.05'}), 400

        # Check if Random Error (Biological Perturbation) mode is enabled
        enable_random_error = data.get('enable_random_error', False)

        # Check if Compare with Baseline mode is enabled
        compare_baseline = data.get('compare_baseline', False)

        # Check if Export Snapshots is enabled
        export_snapshots = data.get('export_snapshots', False)

        # Note: Biological Heatmap is now always generated (checkbox only controls frontend display)
        # Parameter kept for backwards compatibility but is ignored
        show_biological_heatmap = data.get('show_biological_heatmap', False)
        print(f"[DEBUG API] show_biological_heatmap parameter received (ignored, always generates): {show_biological_heatmap}")

        # ALWAYS extract Random Error parameters (will be used with enabled=True/False)
        re_strength = float(data.get('re_strength', 0.03))
        re_duration = int(data.get('re_duration', 30))
        re_frequency = float(data.get('re_frequency', 0.05))
        re_probability = float(data.get('re_probability', 0.05))
        re_num_regions = int(data.get('re_num_regions', 3))
        re_region_size = int(data.get('re_region_size', 10))
        re_jitter = float(data.get('re_jitter', 0.10))
        re_micro_noise = float(data.get('re_micro_noise', 0.05))
        re_alpha_var = float(data.get('re_alpha_var', 0.20))

        # Provide Random Error params, using request values or preset fallbacks
        re_beta = float(data.get('re_beta', preset_params.get('re_beta', 0.10)))
        re_drift_x = float(data.get('re_drift_x', preset_params.get('re_drift_x', 1.2)))
        re_drift_y = float(data.get('re_drift_y', preset_params.get('re_drift_y', 1.0)))
        re_drift_freq = float(data.get('re_drift_frequency', preset_params.get('re_drift_frequency', 0.002)))

        # Create Random Error params (enabled based on checkbox)
        random_error_params = create_random_error_params(
            enabled=enable_random_error,
            strength=re_strength,
            duration=re_duration,
            frequency=re_frequency,
            probability=re_probability,
            num_regions=re_num_regions,
            region_size=re_region_size,
            jitter=re_jitter,
            micro_noise=re_micro_noise,
            alpha_var=re_alpha_var,
            beta=re_beta,
            drift_x=re_drift_x,
            drift_y=re_drift_y,
            drift_frequency=re_drift_freq
        )

        # Compare with Baseline mode (archived feature, kept for compatibility)
        if compare_baseline and enable_random_error:
                # Generate BOTH baseline and perturbed textures for comparison

                # 1. Generate baseline (no Random Error)
                baseline_params = create_random_error_params(enabled=False)
                baseline_path = texture_service.generate_with_biological_perturbation(
                    K=params['K'],
                    t_max=params['t_max'],
                    delta_t=params['delta_t'],
                    color1=params['color1'],
                    color2=params['color2'],
                    params_override=preset_params,
                    random_error_params=baseline_params,
                    export_snapshots=False  # No snapshots for baseline
                )

                # 2. Generate perturbed texture (with Random Error)
                perturbed_path = texture_service.generate_with_biological_perturbation(
                    K=params['K'],
                    t_max=params['t_max'],
                    delta_t=params['delta_t'],
                    color1=params['color1'],
                    color2=params['color2'],
                    params_override=preset_params,
                    random_error_params=random_error_params,
                    export_snapshots=export_snapshots
                )

                # Return both URLs
                baseline_filename = os.path.basename(baseline_path)
                perturbed_filename = os.path.basename(perturbed_path)
                baseline_url = url_for('static', filename=f'images/{baseline_filename}', _external=True)
                perturbed_url = url_for('static', filename=f'images/{perturbed_filename}', _external=True)

                response = {
                    'baseline_url': baseline_url,
                    'perturbed_url': perturbed_url
                }

                # Add snapshots if exported
                if export_snapshots:
                    # Find snapshot files (pattern: snapshot_stepXXXX.png)
                    snapshot_pattern = os.path.join(IMAGES_DIR, 'snapshot_step*.png')
                    snapshot_files = sorted(glob.glob(snapshot_pattern))[-4:]  # Get last 4 snapshots
                    snapshot_urls = [url_for('static', filename=f'images/{os.path.basename(f)}', _external=True)
                                    for f in snapshot_files]
                    response['snapshots'] = snapshot_urls
                    print(f"[API] Returning {len(snapshot_urls)} snapshot URLs (Random Error + Baseline comparison mode)")

                return jsonify(response)

        # Standard texture generation (always use biological perturbation method)
        # Random Error will be enabled/disabled based on random_error_params
        image_path = texture_service.generate_with_biological_perturbation(
            K=params['K'],
            t_max=params['t_max'],
            delta_t=params['delta_t'],
            color1=params['color1'],
            color2=params['color2'],
            params_override=preset_params,
            random_error_params=random_error_params,
            export_snapshots=export_snapshots
        )

        # Return image URL
        filename = os.path.basename(image_path)
        image_url = url_for('static', filename=f'images/{filename}', _external=True)
        response = {'image_url': image_url}

        # Add snapshots if exported
        if export_snapshots:
            # Find snapshot files (pattern: snapshot_stepXXXX.png)
            snapshot_pattern = os.path.join(IMAGES_DIR, 'snapshot_step*.png')
            snapshot_files = sorted(glob.glob(snapshot_pattern))[-4:]
            snapshot_urls = [url_for('static', filename=f'images/{os.path.basename(f)}', _external=True)
                            for f in snapshot_files]
            response['snapshots'] = snapshot_urls
            print(f"[API] Returning {len(snapshot_urls)} snapshot URLs")

        return jsonify(response)
    
    except Exception as e:
        # Log error and return user-friendly message
        return jsonify({'error': str(e)}), 500

def _generate_23_response():
    """
    Generate Figure 2.3 stripe texture using a small local parameter sweep.

    Expected JSON:
    {
        "stage": int,      # 1..5
        "stripe_variant": "baseline|mild_modulation|moderate_modulation",
        "color1": "#RRGGBB",
        "color2": "#RRGGBB"
    }
    """
    try:
        data = request.get_json() or {}
        color1 = str(data.get('color1', '#f3e7c6'))
        color2 = str(data.get('color2', '#101010'))
        parameter_mode = str(data.get('parameter_mode', 'static')).strip().lower()
        params_override = data.get('params_override') or {}
        if not isinstance(params_override, dict):
            params_override = {}
        spatial_modulation_override = data.get('spatial_modulation_override') or {}
        if not isinstance(spatial_modulation_override, dict):
            spatial_modulation_override = {}
        if not (len(color1) == 7 and color1.startswith('#')):
            return jsonify({'error': 'color1 must be HEX format #RRGGBB'}), 400
        if not (len(color2) == 7 and color2.startswith('#')):
            return jsonify({'error': 'color2 must be HEX format #RRGGBB'}), 400

        progression_level_raw = data.get('progression_level')
        if progression_level_raw is not None:
            progression_level = str(progression_level_raw).strip().lower()
            if progression_level not in FIG23_PROGRESSION_LEVELS:
                return jsonify({'error': 'progression_level must be one of malo, vice, jeste_vice, nejvice'}), 400

            level_spec = dict(FIG23_PROGRESSION_LEVELS[progression_level])
            progress_percent = int(level_spec.get('progress_percent', 60))
            development_key = str(level_spec.get('development_key', 'dev_60'))
            random_error_defaults = dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS.get(development_key, {}))
            random_error_defaults.update(dict(level_spec.get('random_error_override', {})))
            enable_random_error = bool(data.get('enable_random_error', False))
            random_error_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', random_error_defaults.get('strength', 0.01))),
                duration=int(data.get('re_duration', random_error_defaults.get('duration', 12))),
                frequency=float(data.get('re_frequency', random_error_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', random_error_defaults.get('probability', 0.02))),
                num_regions=int(data.get('re_num_regions', random_error_defaults.get('num_regions', 1))),
                region_size=int(data.get('re_region_size', random_error_defaults.get('region_size', 8))),
                jitter=float(data.get('re_jitter', random_error_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', random_error_defaults.get('micro_noise', 0.04))),
                alpha_var=float(data.get('re_alpha_var', random_error_defaults.get('alpha_var', 0.20))),
                beta=float(data.get('re_beta', random_error_defaults.get('beta', 0.08))),
                drift_x=float(data.get('re_drift_x', random_error_defaults.get('drift_x', 0.8))),
                drift_y=float(data.get('re_drift_y', random_error_defaults.get('drift_y', 0.8))),
                drift_frequency=float(data.get('re_drift_frequency', random_error_defaults.get('drift_frequency', 0.002))),
                disturbance_kind='stripe',
                local_y_segments=bool(random_error_defaults.get('local_y_segments', True)),
            )
            image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
                development_percent=progress_percent,
                params_override={
                    **level_spec.get('params_override', {}),
                    **(params_override if parameter_mode == 'dynamic' else {}),
                },
                spatial_modulation_override={
                    **level_spec.get('spatial_modulation', {}),
                    **(spatial_modulation_override if parameter_mode == 'dynamic' else {}),
                },
                random_error_params=random_error_params,
                color1=color1,
                color2=color2,
                size=DEFAULT_TEXTURE_SIZE,
                export_snapshots=True,
            )
            mode_result = getattr(texture_service, 'last_mode_result', None)
            if mode_result is None or not getattr(mode_result, 'snapshots', None):
                return jsonify({'error': 'Stripe progression rendering failed'}), 500

            suffix = hashlib.sha1(
                f"figure_2_3|{progression_level}|{color1}|{color2}|{progress_percent}".encode('utf-8')
            ).hexdigest()[:10]
            space_time_filename = f"figure_2_3_{progression_level}_{suffix}_space_time.png"
            space_time_path = os.path.join(IMAGES_DIR, space_time_filename)
            save_stripe_space_time_image(mode_result.snapshots, space_time_path)
            texture_filename = os.path.basename(image_path)

            return jsonify({
                'mode': 'stable_periodic_patterns',
                'preset': progression_level,
                'progression_level': progression_level,
                'label': level_spec.get('label', progression_level),
                'reference_report': level_spec.get('reference_report', ''),
                'progress_percent': progress_percent,
                'image_url': url_for('static', filename=f'images/{texture_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'download_name': f"figure_2_3_{progression_level}.png",
                'space_time_url': url_for('static', filename=f'images/{space_time_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'space_time_download_name': f"figure_2_3_{progression_level}_space_time.png",
                'progression_spec': {
                    'label': level_spec.get('label', progression_level),
                    'reference_report': level_spec.get('reference_report', ''),
                    'progress_percent': progress_percent,
                    'development_key': development_key,
                    't_max': level_spec.get('t_max'),
                    'params_override': level_spec.get('params_override', {}),
                },
                'random_error_enabled': bool(random_error_params.get('enabled', False)),
                'random_error_profile': random_error_params,
                'parameter_mode': parameter_mode,
                'applied_params_override': params_override if parameter_mode == 'dynamic' else {},
                'applied_spatial_modulation_override': spatial_modulation_override if parameter_mode == 'dynamic' else {},
            })

        stripe_variant_raw = data.get('stripe_variant')
        if stripe_variant_raw is not None:
            stripe_variant = str(stripe_variant_raw).strip().lower()
            if stripe_variant not in FIG23_STRIPE_VARIANTS:
                return jsonify({
                    'error': 'stripe_variant must be one of baseline, mild_modulation, moderate_modulation'
                }), 400

            variant_spec = dict(FIG23_STRIPE_VARIANTS[stripe_variant])
            base_stage_key = str(variant_spec.get('base_stage', 'stage_3'))
            base_stage_spec = dict(FIG23_STAGE_PRESETS[base_stage_key])
            enable_random_error = bool(data.get('enable_random_error', False))
            random_error_defaults = dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS.get('dev_60', {}))
            random_error_defaults.update(dict(variant_spec.get('random_error_override', {})))
            random_error_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', random_error_defaults.get('strength', 0.01))),
                duration=int(data.get('re_duration', random_error_defaults.get('duration', 12))),
                frequency=float(data.get('re_frequency', random_error_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', random_error_defaults.get('probability', 0.02))),
                num_regions=int(data.get('re_num_regions', random_error_defaults.get('num_regions', 1))),
                region_size=int(data.get('re_region_size', random_error_defaults.get('region_size', 8))),
                jitter=float(data.get('re_jitter', random_error_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', random_error_defaults.get('micro_noise', 0.04))),
                alpha_var=float(data.get('re_alpha_var', random_error_defaults.get('alpha_var', 0.20))),
                beta=float(data.get('re_beta', random_error_defaults.get('beta', 0.08))),
                drift_x=float(data.get('re_drift_x', random_error_defaults.get('drift_x', 0.8))),
                drift_y=float(data.get('re_drift_y', random_error_defaults.get('drift_y', 0.8))),
                drift_frequency=float(data.get('re_drift_frequency', random_error_defaults.get('drift_frequency', 0.002))),
                disturbance_kind='stripe',
                local_y_segments=bool(random_error_defaults.get('local_y_segments', True)),
            )
            image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
                stripe_variant=stripe_variant,
                params_override={
                    **variant_spec.get('params_override', {}),
                    **(params_override if parameter_mode == 'dynamic' else {}),
                },
                spatial_modulation_override={
                    **variant_spec.get('spatial_modulation', {}),
                    **(spatial_modulation_override if parameter_mode == 'dynamic' else {}),
                },
                random_error_params=random_error_params,
                color1=color1,
                color2=color2,
                size=DEFAULT_TEXTURE_SIZE,
                export_snapshots=True,
            )
            mode_result = getattr(texture_service, 'last_mode_result', None)
            if mode_result is None or not getattr(mode_result, 'snapshots', None):
                return jsonify({'error': 'Stripe progression rendering failed'}), 500

            suffix = hashlib.sha1(
                f"figure_2_3|{stripe_variant}|{color1}|{color2}|{base_stage_key}".encode('utf-8')
            ).hexdigest()[:10]
            space_time_filename = f"figure_2_3_{stripe_variant}_{suffix}_space_time.png"
            space_time_path = os.path.join(IMAGES_DIR, space_time_filename)
            save_stripe_space_time_image(mode_result.snapshots, space_time_path)
            texture_filename = os.path.basename(image_path)

            return jsonify({
                'mode': 'stable_periodic_patterns',
                'preset': stripe_variant,
                'stripe_variant': stripe_variant,
                'label': variant_spec.get('label', stripe_variant),
                'reference_report': variant_spec.get('reference_report', ''),
                'image_url': url_for('static', filename=f'images/{texture_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'download_name': f"figure_2_3_{stripe_variant}.png",
                'space_time_url': url_for('static', filename=f'images/{space_time_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'space_time_download_name': f"figure_2_3_{stripe_variant}_space_time.png",
                'progression_spec': {
                    'label': variant_spec.get('label', stripe_variant),
                    'reference_report': variant_spec.get('reference_report', ''),
                    'development_key': variant_spec.get('base_stage', ''),
                },
                'random_error_enabled': bool(random_error_params.get('enabled', False)),
                'random_error_profile': random_error_params,
                'parameter_mode': parameter_mode,
                'applied_params_override': params_override if parameter_mode == 'dynamic' else {},
                'applied_spatial_modulation_override': spatial_modulation_override if parameter_mode == 'dynamic' else {},
            })

        stage_raw = data.get('stage')
        if stage_raw is not None:
            stage = int(stage_raw)
            if stage not in [1, 2, 3, 4, 5]:
                return jsonify({'error': 'stage must be in [1,2,3,4,5]'}), 400
            stage_key = f"stage_{stage}"
            stage_spec = dict(FIG23_STAGE_PRESETS[stage_key])
            stage_re_defaults = dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS.get('dev_60', {}))
            random_error_params = create_random_error_params(
                enabled=bool(data.get('enable_random_error', False)),
                strength=float(data.get('re_strength', stage_re_defaults.get('strength', 0.01))),
                duration=int(data.get('re_duration', stage_re_defaults.get('duration', 12))),
                frequency=float(data.get('re_frequency', stage_re_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', stage_re_defaults.get('probability', 0.02))),
                num_regions=int(data.get('re_num_regions', stage_re_defaults.get('num_regions', 1))),
                region_size=int(data.get('re_region_size', stage_re_defaults.get('region_size', 8))),
                jitter=float(data.get('re_jitter', stage_re_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', stage_re_defaults.get('micro_noise', 0.04))),
                alpha_var=float(data.get('re_alpha_var', stage_re_defaults.get('alpha_var', 0.20))),
                beta=float(data.get('re_beta', stage_re_defaults.get('beta', 0.08))),
                drift_x=float(data.get('re_drift_x', stage_re_defaults.get('drift_x', 0.8))),
                drift_y=float(data.get('re_drift_y', stage_re_defaults.get('drift_y', 0.8))),
                drift_frequency=float(data.get('re_drift_frequency', stage_re_defaults.get('drift_frequency', 0.002))),
                disturbance_kind='stripe',
                local_y_segments=bool(stage_re_defaults.get('local_y_segments', True)),
            )
            image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
                stage=stage,
                params_override={
                    **stage_spec.get('params_override', {}),
                    **(params_override if parameter_mode == 'dynamic' else {}),
                },
                spatial_modulation_override=stage_spec.get('spatial_modulation', {}),
                random_error_params=random_error_params,
                color1=color1,
                color2=color2,
                size=DEFAULT_TEXTURE_SIZE,
                export_snapshots=True,
            )
            mode_result = getattr(texture_service, 'last_mode_result', None)
            if mode_result is None or not getattr(mode_result, 'snapshots', None):
                return jsonify({'error': 'Stripe progression rendering failed'}), 500

            suffix = hashlib.sha1(
                f"figure_2_3|{stage_key}|{color1}|{color2}|{stage}".encode('utf-8')
            ).hexdigest()[:10]
            space_time_filename = f"figure_2_3_{stage_key}_{suffix}_space_time.png"
            space_time_path = os.path.join(IMAGES_DIR, space_time_filename)
            save_stripe_space_time_image(mode_result.snapshots, space_time_path)
            texture_filename = os.path.basename(image_path)

            return jsonify({
                'mode': 'stable_periodic_patterns',
                'preset': stage_key,
                'stage': stage,
                'label': stage_spec.get('label', stage_key),
                'reference_report': stage_spec.get('reference_report', ''),
                'image_url': url_for('static', filename=f'images/{texture_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'download_name': f"figure_2_3_{stage_key}.png",
                'space_time_url': url_for('static', filename=f'images/{space_time_filename}', _external=True) + f'?v={int(time.time() * 1000)}',
                'space_time_download_name': f"figure_2_3_{stage_key}_space_time.png",
                'stage_spec': {
                    'label': stage_spec.get('label', stage_key),
                    'reference_report': stage_spec.get('reference_report', ''),
                    'params_override': stage_spec.get('params_override', {}),
                },
                'random_error_enabled': bool(random_error_params.get('enabled', False)),
                'random_error_profile': random_error_params,
                'parameter_mode': parameter_mode,
                'applied_params_override': params_override if parameter_mode == 'dynamic' else {},
                'applied_spatial_modulation_override': spatial_modulation_override if parameter_mode == 'dynamic' else {},
            })

        stripe_variant_raw = data.get('stripe_variant')
        if stripe_variant_raw is not None:
            stripe_variant = str(stripe_variant_raw).strip().lower()
            if stripe_variant not in FIG23_STRIPE_VARIANTS:
                return jsonify({
                    'error': 'stripe_variant must be one of baseline, mild_modulation, moderate_modulation'
                }), 400

            variant_spec = dict(FIG23_STRIPE_VARIANTS[stripe_variant])
            base_stage_key = str(variant_spec.get('base_stage', 'stage_3'))
            base_stage_spec = dict(FIG23_STAGE_PRESETS[base_stage_key])
            enable_random_error = bool(data.get('enable_random_error', False))
            random_error_defaults = dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS.get('dev_60', {}))
            random_error_defaults.update(dict(variant_spec.get('random_error_override', {})))
            random_error_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', random_error_defaults.get('strength', 0.015))),
                duration=int(data.get('re_duration', random_error_defaults.get('duration', 14))),
                frequency=float(data.get('re_frequency', random_error_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', random_error_defaults.get('probability', 0.018))),
                num_regions=int(data.get('re_num_regions', random_error_defaults.get('num_regions', 1))),
                region_size=int(data.get('re_region_size', random_error_defaults.get('region_size', 12))),
                jitter=float(data.get('re_jitter', random_error_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', random_error_defaults.get('micro_noise', 0.04))),
                alpha_var=float(data.get('re_alpha_var', random_error_defaults.get('alpha_var', 0.22))),
                beta=float(data.get('re_beta', random_error_defaults.get('beta', 0.08))),
                drift_x=float(data.get('re_drift_x', random_error_defaults.get('drift_x', 1.0))),
                drift_y=float(data.get('re_drift_y', random_error_defaults.get('drift_y', 0.90))),
                drift_frequency=float(data.get('re_drift_frequency', random_error_defaults.get('drift_frequency', 0.0020))),
                disturbance_kind='stripe',
                local_y_segments=bool(random_error_defaults.get('local_y_segments', False)),
            )

            image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
                stripe_variant=stripe_variant,
                random_error_params=random_error_params,
                color1=color1,
                color2=color2,
                size=DEFAULT_TEXTURE_SIZE,
                export_snapshots=False,
            )
            stripe_result = getattr(texture_service, "last_mode_result", None)

            with Image.open(image_path) as img:
                rgb = np.asarray(img.convert('RGB'), dtype=np.uint8)

            suffix = hashlib.sha1(
                f"figure_2_3|{stripe_variant}|{color1}|{color2}|{variant_spec.get('spatial_modulation', {}).get('eps_s')}|{variant_spec.get('spatial_modulation', {}).get('eps_Da')}".encode('utf-8')
            ).hexdigest()[:10]
            filename = f"figure_2_3_{stripe_variant}_{suffix}.png"
            output_path = os.path.join(IMAGES_DIR, filename)
            Image.fromarray(rgb).save(output_path)

            image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
            raw_image_url = ""
            space_time_url = ""
            if stripe_result is not None and getattr(stripe_result, "raw_image_path", ""):
                raw_image_name = os.path.basename(stripe_result.raw_image_path)
                raw_image_url = url_for('static', filename=f'images/{raw_image_name}', _external=True)
            if stripe_result is not None and getattr(stripe_result, "space_time_path", ""):
                space_time_name = os.path.basename(stripe_result.space_time_path)
                space_time_url = url_for('static', filename=f'images/{space_time_name}', _external=True)
            return jsonify({
                'image_url': image_url,
                'mode': 'stable_periodic_patterns',
                'preset': stripe_variant,
                'stripe_variant': stripe_variant,
                'stage_label': variant_spec.get('label', stripe_variant),
                'download_name': f"figure_2_3_{stripe_variant}.png",
                'random_error_enabled': bool(random_error_params.get('enabled', False)),
                'random_error_profile': random_error_params,
                'stripe_variant_spec': {
                    'label': variant_spec.get('label', stripe_variant),
                    'reference_report': variant_spec.get('reference_report', ''),
                    'base_stage': base_stage_key,
                    'spatial_modulation': variant_spec.get('spatial_modulation', {}),
                },
                'base_stage_spec': {
                    'label': base_stage_spec.get('label', base_stage_key),
                    'reference_report': base_stage_spec.get('reference_report', ''),
                    'params_override': base_stage_spec.get('params_override', {}),
                },
                'raw_image_url': raw_image_url,
                'space_time_url': space_time_url,
            })

        development_percent_raw = data.get('development_percent')
        if development_percent_raw is not None:
            development_percent = int(development_percent_raw)
            preset_key = f'dev_{development_percent}'
            if development_percent not in [10, 30, 60, 90]:
                return jsonify({'error': 'development_percent must be one of 10, 30, 60, 90'}), 400
            development_spec = dict(FIG23_DEVELOPMENT_PRESETS[preset_key])
            params_override = dict(development_spec.get('params_override', {}))
            enable_random_error = bool(data.get('enable_random_error', False))
            random_error_defaults = dict(FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS[preset_key])
            random_error_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', random_error_defaults.get('strength', 0.01))),
                duration=int(data.get('re_duration', random_error_defaults.get('duration', 12))),
                frequency=float(data.get('re_frequency', random_error_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', random_error_defaults.get('probability', 0.02))),
                num_regions=int(data.get('re_num_regions', random_error_defaults.get('num_regions', 1))),
                region_size=int(data.get('re_region_size', random_error_defaults.get('region_size', 8))),
                jitter=float(data.get('re_jitter', random_error_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', random_error_defaults.get('micro_noise', 0.04))),
                alpha_var=float(data.get('re_alpha_var', random_error_defaults.get('alpha_var', 0.20))),
                beta=float(data.get('re_beta', random_error_defaults.get('beta', 0.08))),
                drift_x=float(data.get('re_drift_x', random_error_defaults.get('drift_x', 0.8))),
                drift_y=float(data.get('re_drift_y', random_error_defaults.get('drift_y', 0.8))),
                drift_frequency=float(data.get('re_drift_frequency', random_error_defaults.get('drift_frequency', 0.002))),
                disturbance_kind='stripe',
                local_y_segments=bool(random_error_defaults.get('local_y_segments', False)),
            )

            image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
                development_percent=development_percent,
                random_error_params=random_error_params,
                color1=color1,
                color2=color2,
                size=DEFAULT_TEXTURE_SIZE,
                export_snapshots=False,
            )

            with Image.open(image_path) as img:
                rgb = np.asarray(img.convert('RGB'), dtype=np.uint8)

            suffix = hashlib.sha1(
                f"figure_2_3|{preset_key}|{color1}|{color2}|{params_override.get('D_b')}|{params_override.get('D_a')}|{params_override.get('r_b')}".encode('utf-8')
            ).hexdigest()[:10]
            filename = f"figure_2_3_{preset_key}_{suffix}.png"
            output_path = os.path.join(IMAGES_DIR, filename)
            Image.fromarray(rgb).save(output_path)

            image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
            return jsonify({
                'image_url': image_url,
                'mode': 'stable_periodic_patterns',
                'preset': preset_key,
                'development_percent': development_percent,
                'random_error_enabled': bool(random_error_params.get('enabled', False)),
                'random_error_profile': random_error_params,
                'stage_label': development_spec.get('label', preset_key),
                'download_name': f"figure_2_3_{preset_key}.png",
                'development_spec': {
                    'label': development_spec.get('label', preset_key),
                    'reference_report': development_spec.get('reference_report', ''),
                    'progress_percent': development_spec.get('progress_percent'),
                    't_max': development_spec.get('t_max'),
                    'params_override': params_override,
                }
            })

        stage = int(data.get('stage', FIG23_DEFAULT_STAGE.split('_')[-1]))
        if stage not in [1, 2, 3, 4, 5]:
            return jsonify({'error': 'stage must be in [1,2,3,4,5]'}), 400

        preset_key = f'stage_{stage}'
        stage_spec = dict(FIG23_STAGE_PRESETS[preset_key])
        params_override = dict(stage_spec.get('params_override', {}))

        image_path, _heatmap_data = texture_service.generate_stable_periodic_patterns(
            stage=stage,
            color1=color1,
            color2=color2,
            size=DEFAULT_TEXTURE_SIZE,
            export_snapshots=False,
        )

        with Image.open(image_path) as img:
            rgb = np.asarray(img.convert('RGB'), dtype=np.uint8)

        suffix = hashlib.sha1(
            f"figure_2_3|{preset_key}|{color1}|{color2}|{params_override.get('D_b')}|{params_override.get('D_a')}|{params_override.get('r_b')}".encode('utf-8')
        ).hexdigest()[:10]
        filename = f"figure_2_3_{preset_key}_{suffix}.png"
        output_path = os.path.join(IMAGES_DIR, filename)
        Image.fromarray(rgb).save(output_path)

        image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
        return jsonify({
            'image_url': image_url,
            'mode': 'stable_periodic_patterns',
            'preset': preset_key,
            'stage_label': stage_spec.get('label', preset_key),
            'download_name': f"figure_2_3_{preset_key}.png",
            'stage_spec': {
                'label': stage_spec.get('label', preset_key),
                'reference_report': stage_spec.get('reference_report', ''),
                'params_override': params_override,
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


from routes import api_fig23  # noqa: F401
from routes.api_fig211_212 import register_fig211_212_routes
from routes.api_localized import register_localized_routes
from routes.api_random import register_random_routes
from routes.api_oscillatory import register_oscillatory_routes

register_random_routes(api)
register_fig211_212_routes(api)
register_localized_routes(
    api,
    texture_service=texture_service,
    validate_texture_params=validate_texture_params,
    simulation_presets=SIMULATION_PRESETS,
)
register_oscillatory_routes(api, static_dir=STATIC_DIR)



