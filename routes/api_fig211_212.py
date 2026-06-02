"""Figure 2.11/2.12 API routes extracted from the main API module."""

from __future__ import annotations

import hashlib
import time
from importlib import import_module
from pathlib import Path

import numpy as np
from PIL import Image
from flask import jsonify, request, url_for

from config import DEFAULT_TEXTURE_SIZE
from config_211 import (
    FIG211_DEVELOPMENT_PRESETS,
    FIG211_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    MODEL_211_PARAMS,
    SPOTS_211_PRESETS,
    SPOTS_211_RANDOM_ERROR_PRESETS,
)
from config_212 import (
    FIG212_DEVELOPMENT_PRESETS,
    FIG212_DEVELOPMENT_RANDOM_ERROR_PRESETS,
    FIG212_STAGE_PRESETS,
    RANDOM_ERROR_212_STAGES,
)
from routes.api_fig211_helpers import save_fig211_generated_image
from utils.helpers import hex_to_rgb
from services.random_error_module import create_random_error_params


def _api_module():
    return import_module("routes.api")


def register_fig211_212_routes(api):
    """Register the Figure 2.11 and 2.12 endpoints on the shared API blueprint."""

    @api.route('/api/generate-212', methods=['POST'])
    def generate_212():
        """
        Generate Figure 2.12 activator-inhibitor texture by stage (1-5).

        Expected JSON:
        {
            "stage": int,      # 1..5
            "color1": "#RRGGBB",
            "color2": "#RRGGBB",
            "enable_random_error": bool,   # optional
            "re_strength": float,          # optional
            "re_duration": int,            # optional
            "re_frequency": float,         # optional
            "re_probability": float,       # optional
            "re_num_regions": int,         # optional
            "re_region_size": int          # optional
        }
        """
        try:
            api_module = _api_module()
            texture_service = api_module.texture_service
            default_texture_size = getattr(api_module, "DEFAULT_TEXTURE_SIZE", DEFAULT_TEXTURE_SIZE)

            data = request.get_json() or {}
            color1 = str(data.get('color1', '#ffffff'))
            color2 = str(data.get('color2', '#000000'))
            parameter_mode = str(data.get('parameter_mode', 'static')).strip().lower()
            params_override = data.get('params_override') or {}
            if not isinstance(params_override, dict):
                params_override = {}

            if not (len(color1) == 7 and color1.startswith('#')):
                return jsonify({'error': 'color1 must be HEX format #RRGGBB'}), 400
            if not (len(color2) == 7 and color2.startswith('#')):
                return jsonify({'error': 'color2 must be HEX format #RRGGBB'}), 400

            development_percent_raw = data.get('development_percent')
            if development_percent_raw is not None:
                development_percent = int(development_percent_raw)
                development_key = f'dev_{development_percent}'
                if development_percent not in [10, 30, 60, 90]:
                    return jsonify({'error': 'development_percent must be one of 10, 30, 60, 90'}), 400

                development_spec = dict(FIG212_DEVELOPMENT_PRESETS[development_key])
                stage_key = str(development_spec.get('stage_key', 'stage_3'))
                stage = int(stage_key.split('_')[-1])
                stage_spec = dict(FIG212_STAGE_PRESETS[stage_key])
                stage_re_defaults = dict(FIG212_DEVELOPMENT_RANDOM_ERROR_PRESETS[development_key])
                enable_random_error = bool(data.get('enable_random_error', False))
                re_params = create_random_error_params(
                    enabled=enable_random_error,
                    strength=float(data.get('re_strength', stage_re_defaults.get('strength', 0.01))),
                    duration=int(data.get('re_duration', stage_re_defaults.get('duration', 10))),
                    frequency=float(data.get('re_frequency', stage_re_defaults.get('frequency', 0.05))),
                    probability=float(data.get('re_probability', stage_re_defaults.get('probability', 0.05))),
                    num_regions=int(data.get('re_num_regions', stage_re_defaults.get('num_regions', 3))),
                    region_size=int(data.get('re_region_size', stage_re_defaults.get('region_size', 15))),
                    jitter=float(data.get('re_jitter', stage_re_defaults.get('jitter', 0.10))),
                    micro_noise=float(data.get('re_micro_noise', stage_re_defaults.get('micro_noise', 0.05))),
                    alpha_var=float(data.get('re_alpha_var', stage_re_defaults.get('alpha_var', 0.20))),
                    beta=float(data.get('re_beta', stage_re_defaults.get('beta', 0.10))),
                    drift_x=float(data.get('re_drift_x', stage_re_defaults.get('drift_x', 1.0))),
                    drift_y=float(data.get('re_drift_y', stage_re_defaults.get('drift_y', 1.0))),
                    drift_frequency=float(data.get('re_drift_frequency', stage_re_defaults.get('drift_frequency', 0.002))),
                    disturbance_kind='labyrinth',
                )
                image_path = texture_service.generate_labyrinths(
                    stage=stage,
                    color1=color1,
                    color2=color2,
                    params_override=params_override if parameter_mode == 'dynamic' else None,
                    random_error_params=re_params,
                )
                filename = Path(image_path).name
                image_url = url_for('static', filename=f'images/{filename}', _external=True)
                return jsonify({
                    'image_url': image_url,
                    'mode': 'labyrinths',
                    'preset': development_key,
                    'development_percent': development_percent,
                    'random_error_enabled': bool(re_params.get('enabled', False)),
                    'random_error_profile': re_params,
                    'stage': stage,
                    'stage_label': development_spec.get('label', development_key),
                    'download_name': f"figure_2_12_{development_key}.png",
                    'development_spec': {
                        'label': development_spec.get('label', development_key),
                        'reference_report': development_spec.get('reference_report', ''),
                        'progress_percent': development_spec.get('progress_percent'),
                        'stage_key': stage_key,
                    },
                    'stage_spec': {
                        'label': stage_spec.get('label', stage_key),
                        'reference_report': stage_spec.get('reference_report', ''),
                    },
                    'applied_re_params': {
                        'enabled': bool(re_params.get('enabled', False)),
                        'strength': float(re_params.get('strength', 0.0)),
                        'duration': int(re_params.get('duration', 0)),
                        'frequency': float(re_params.get('frequency', 0.0)),
                        'probability': float(re_params.get('probability', 0.0)),
                        'num_regions': int(re_params.get('num_regions', 0)),
                        'region_size': int(re_params.get('region_size', 0)),
                    },
                })

            stage = int(data.get('stage', 3))
            enable_random_error = bool(data.get('enable_random_error', False))

            if stage not in [1, 2, 3, 4, 5]:
                return jsonify({'error': 'stage must be in [1,2,3,4,5]'}), 400

            stage_key = f"stage_{stage}"
            stage_spec = dict(FIG212_STAGE_PRESETS[stage_key])
            stage_re_defaults = dict(RANDOM_ERROR_212_STAGES.get(stage_key, {}))
            re_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', stage_re_defaults.get('strength', 0.01))),
                duration=int(data.get('re_duration', stage_re_defaults.get('duration', 10))),
                frequency=float(data.get('re_frequency', stage_re_defaults.get('frequency', 0.05))),
                probability=float(data.get('re_probability', stage_re_defaults.get('probability', 0.05))),
                num_regions=int(data.get('re_num_regions', stage_re_defaults.get('num_regions', 3))),
                region_size=int(data.get('re_region_size', stage_re_defaults.get('region_size', 15))),
                jitter=float(data.get('re_jitter', stage_re_defaults.get('jitter', 0.10))),
                micro_noise=float(data.get('re_micro_noise', stage_re_defaults.get('micro_noise', 0.05))),
                alpha_var=float(data.get('re_alpha_var', stage_re_defaults.get('alpha_var', 0.20))),
                beta=float(data.get('re_beta', stage_re_defaults.get('beta', 0.10))),
                drift_x=float(data.get('re_drift_x', stage_re_defaults.get('drift_x', 1.0))),
                drift_y=float(data.get('re_drift_y', stage_re_defaults.get('drift_y', 1.0))),
                drift_frequency=float(data.get('re_drift_frequency', stage_re_defaults.get('drift_frequency', 0.002))),
                disturbance_kind='labyrinth',
            )

            image_path = texture_service.generate_labyrinths(
                stage=stage,
                color1=color1,
                color2=color2,
                params_override=params_override if parameter_mode == 'dynamic' else None,
                random_error_params=re_params,
            )
            filename = Path(image_path).name
            image_url = url_for('static', filename=f'images/{filename}', _external=True)
            return jsonify({
                'image_url': image_url,
                'mode': 'labyrinths',
                'preset': stage_key,
                'stage': stage,
                'stage_label': stage_spec.get('label', stage_key),
                'random_error_enabled': bool(re_params.get('enabled', False)),
                'random_error_profile': re_params,
                'applied_re_params': {
                    'enabled': bool(re_params.get('enabled', False)),
                    'strength': float(re_params.get('strength', 0.0)),
                    'duration': int(re_params.get('duration', 0)),
                    'frequency': float(re_params.get('frequency', 0.0)),
                    'probability': float(re_params.get('probability', 0.0)),
                    'num_regions': int(re_params.get('num_regions', 0)),
                    'region_size': int(re_params.get('region_size', 0)),
                },
                'stage_spec': {
                    'label': stage_spec.get('label', stage_key),
                    'reference_report': stage_spec.get('reference_report', ''),
                }
            })
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api.route('/api/generate-211', methods=['POST'])
    def generate_211():
        """
        Generate Figure 2.11 spot texture using the Meinhardt baseline.

        Expected JSON:
        {
            "preset": "balanced|soft|dense|wide",
            "color1": "#RRGGBB",
            "color2": "#RRGGBB"
        }
        """
        try:
            api_module = _api_module()
            texture_service = api_module.texture_service
            images_dir = api_module.IMAGES_DIR
            default_texture_size = getattr(api_module, "DEFAULT_TEXTURE_SIZE", DEFAULT_TEXTURE_SIZE)
            colorize_fig211_stage = getattr(api_module, "_colorize_fig211_stage")
            apply_fig211_random_error = getattr(api_module, "_apply_fig211_random_error")

            data = request.get_json() or {}
            color1 = str(data.get('color1', '#d9d9d9'))
            color2 = str(data.get('color2', '#2b2b2b'))
            parameter_mode = str(data.get('parameter_mode', 'static')).strip().lower()
            params_override = data.get('params_override') or {}
            if not isinstance(params_override, dict):
                params_override = {}

            if not (len(color1) == 7 and color1.startswith('#')):
                return jsonify({'error': 'color1 must be HEX format #RRGGBB'}), 400
            if not (len(color2) == 7 and color2.startswith('#')):
                return jsonify({'error': 'color2 must be HEX format #RRGGBB'}), 400

            development_percent_raw = data.get('development_percent')
            if development_percent_raw is not None:
                development_percent = int(development_percent_raw)
                development_key = f'dev_{development_percent}'
                if development_percent not in [10, 30, 60, 90]:
                    return jsonify({'error': 'development_percent must be one of 10, 30, 60, 90'}), 400

                development_spec = dict(FIG211_DEVELOPMENT_PRESETS[development_key])
                preset_key = str(development_spec.get('stage_key', 'stage_2'))
                preset_spec = dict(SPOTS_211_PRESETS[preset_key])
                enable_random_error = bool(data.get('enable_random_error', False))
                random_error_defaults = dict(FIG211_DEVELOPMENT_RANDOM_ERROR_PRESETS[development_key])
                random_error_params = create_random_error_params(
                    enabled=enable_random_error,
                    strength=float(data.get('re_strength', random_error_defaults.get('strength', 0.03))),
                    duration=int(data.get('re_duration', random_error_defaults.get('duration', 30))),
                    frequency=float(data.get('re_frequency', random_error_defaults.get('frequency', 0.05))),
                    probability=float(data.get('re_probability', random_error_defaults.get('probability', 0.05))),
                    num_regions=int(data.get('re_num_regions', random_error_defaults.get('num_regions', 3))),
                    region_size=int(data.get('re_region_size', random_error_defaults.get('region_size', 10))),
                    jitter=float(data.get('re_jitter', random_error_defaults.get('jitter', 0.10))),
                    micro_noise=float(data.get('re_micro_noise', random_error_defaults.get('micro_noise', 0.05))),
                    alpha_var=float(data.get('re_alpha_var', random_error_defaults.get('alpha_var', 0.20))),
                    beta=float(data.get('re_beta', random_error_defaults.get('beta', 0.10))),
                    drift_x=float(data.get('re_drift_x', random_error_defaults.get('drift_x', 1.2))),
                    drift_y=float(data.get('re_drift_y', random_error_defaults.get('drift_y', 1.0))),
                    drift_frequency=float(data.get('re_drift_frequency', random_error_defaults.get('drift_frequency', 0.002))),
                    disturbance_kind='spots',
                )

                image_path = colorize_fig211_stage(texture_service, preset_key, color1, color2)
                with Image.open(image_path) as img:
                    gray = np.asarray(img.convert('L'), dtype=np.float32) / 255.0
                if enable_random_error:
                    gray = apply_fig211_random_error(gray, preset_key, random_error_params)
                    bg_rgb = np.array(hex_to_rgb(color1), dtype=np.float32)
                    spot_rgb = np.array(hex_to_rgb(color2), dtype=np.float32)
                    spot_strength = np.clip(0.15 + 0.70 * (1.0 - gray), 0.0, 1.0)
                    rgb = (
                        bg_rgb[None, None, :] * (1.0 - spot_strength[..., None]) +
                        spot_rgb[None, None, :] * spot_strength[..., None]
                    )
                    rgb = np.clip(rgb, 0.0, 1.0)
                    image_path = save_fig211_generated_image(rgb, development_key, color1, color2, tag='re')
                filename = Path(image_path).name
                image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
                return jsonify({
                    'image_url': image_url,
                    'mode': 'spots',
                    'preset': development_key,
                    'development_percent': development_percent,
                    'random_error_enabled': bool(random_error_params.get('enabled', False)),
                    'random_error_profile': random_error_params,
                    'stage_label': development_spec.get('label', development_key),
                    'download_name': f"figure_2_11_{development_key}.png",
                    'development_spec': {
                        'label': development_spec.get('label', development_key),
                        'reference_report': development_spec.get('reference_report', ''),
                        'progress_percent': development_spec.get('progress_percent'),
                        'stage_key': preset_key,
                        'reference_step': development_spec.get('reference_step', 0),
                        'reference_t': development_spec.get('reference_t', 0.0),
                    },
                    'stage_spec': {
                        'label': preset_spec.get('label', preset_key),
                        'reference_report': preset_spec.get('reference_report', ''),
                        'reference_step': preset_spec.get('reference_step', 0),
                        'reference_t': preset_spec.get('reference_t', 0.0),
                    },
                })

            stage_raw = data.get('stage')
            preset_key = None
            if stage_raw is not None:
                stage = int(stage_raw)
                if stage not in [1, 2, 3, 4]:
                    return jsonify({'error': 'stage must be in [1,2,3,4]'}), 400
                preset_key = f'stage_{stage}'
            else:
                preset_alias = (data.get('preset') or '').strip().lower()
                alias_map = {
                    'balanced': 'stage_3',
                    'soft': 'stage_1',
                    'dense': 'stage_3',
                    'wide': 'stage_4',
                }
                preset_key = alias_map.get(preset_alias, preset_alias or 'stage_3')
                if preset_key not in SPOTS_211_PRESETS:
                    preset_key = 'stage_3'
            preset_spec = dict(SPOTS_211_PRESETS[preset_key])
            enable_random_error = bool(data.get('enable_random_error', False))
            random_error_defaults = dict(SPOTS_211_RANDOM_ERROR_PRESETS[preset_key])
            random_error_params = create_random_error_params(
                enabled=enable_random_error,
                strength=float(data.get('re_strength', random_error_defaults['strength'])),
                duration=int(data.get('re_duration', random_error_defaults['duration'])),
                frequency=float(data.get('re_frequency', random_error_defaults['frequency'])),
                probability=float(data.get('re_probability', random_error_defaults['probability'])),
                num_regions=int(data.get('re_num_regions', random_error_defaults['num_regions'])),
                region_size=int(data.get('re_region_size', random_error_defaults['region_size'])),
                jitter=float(data.get('re_jitter', random_error_defaults['jitter'])),
                micro_noise=float(data.get('re_micro_noise', random_error_defaults['micro_noise'])),
                alpha_var=float(data.get('re_alpha_var', random_error_defaults['alpha_var'])),
                beta=float(data.get('re_beta', random_error_defaults['beta'])),
                drift_x=float(data.get('re_drift_x', random_error_defaults['drift_x'])),
                drift_y=float(data.get('re_drift_y', random_error_defaults['drift_y'])),
                drift_frequency=float(data.get('re_drift_frequency', random_error_defaults['drift_frequency'])),
                disturbance_kind='spots',
            )

            base_params = dict(MODEL_211_PARAMS.get('params', {}))
            base_params.update(dict(preset_spec.get('params_override', {})))

            if parameter_mode == 'dynamic':
                base_params.update(params_override)

            if parameter_mode == 'dynamic':
                output_tag = 're' if enable_random_error else 'dyn'
                output_hash = hashlib.sha1(
                    f"{preset_key}|{output_tag}|{color1}|{color2}|{base_params.get('K')}|{base_params.get('t_max')}|{base_params.get('delta_t')}".encode('utf-8')
                ).hexdigest()[:10]
                output_filename = f"figure_2_11_{preset_key}_{output_tag}_{output_hash}.png"
            else:
                output_filename = None

            if parameter_mode == 'dynamic':
                base_params = dict(base_params)
                base_params['t_max'] = float(base_params.get('t_max', MODEL_211_PARAMS['params'].get('t_max', 5000.0)))

                sim_image_path, _ = texture_service.generate_activator_inhibitor(
                    K=float(base_params.get('K', MODEL_211_PARAMS['params'].get('K', 1.0))),
                    t_max=float(base_params.get('t_max', MODEL_211_PARAMS['params'].get('t_max', 5000.0))),
                    delta_t=float(base_params.get('dt', base_params.get('delta_t', MODEL_211_PARAMS['params'].get('dt', 0.1)))),
                    color1=color1,
                    color2=color2,
                    size=int(base_params.get('size', MODEL_211_PARAMS['params'].get('size', default_texture_size))),
                    preset_name=preset_key,
                    params_override=base_params,
                    random_error_params=random_error_params if enable_random_error else None,
                    export_snapshots=False,
                    output_filename=output_filename,
                    cleanup_prefix=f"figure_2_11_{preset_key}",
                )
                filename = Path(sim_image_path).name
                image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
                response = {
                    'image_url': image_url,
                    'mode': 'spots',
                    'preset': preset_key,
                    'stage_label': preset_spec.get('label', preset_key),
                    'reference_step': int(preset_spec.get('reference_step', 0)),
                    'download_name': f"figure_2_11_{preset_key}.png",
                    'random_error_enabled': enable_random_error,
                    'random_error_profile': random_error_params if enable_random_error else None,
                    'stage_spec': {
                        'label': preset_spec.get('label', preset_key),
                        'reference_report': preset_spec.get('reference_report', ''),
                        'reference_step': preset_spec.get('reference_step', 0),
                        'reference_t': preset_spec.get('reference_t', 0.0),
                    },
                    'applied_params_override': base_params,
                }
                response['parameter_mode'] = 'dynamic'
                return jsonify(response)

            compute_t_max = float(preset_spec.get('reference_t', base_params.get('t_max', MODEL_211_PARAMS['params'].get('t_max', 5000.0))))
            sim_image_path, _ = texture_service.generate_activator_inhibitor(
                K=float(base_params.get('K', MODEL_211_PARAMS['params'].get('K', 1.0))),
                t_max=compute_t_max,
                delta_t=float(base_params.get('dt', base_params.get('delta_t', MODEL_211_PARAMS['params'].get('dt', 0.1)))),
                color1=color1,
                color2=color2,
                size=int(base_params.get('size', MODEL_211_PARAMS['params'].get('size', default_texture_size))),
                preset_name=preset_key,
                params_override=base_params,
                random_error_params=random_error_params if enable_random_error else None,
                export_snapshots=False,
                output_filename=output_filename,
                cleanup_prefix=f"figure_2_11_{preset_key}",
            )
            filename = Path(sim_image_path).name
            image_url = url_for('static', filename=f'images/{filename}', _external=True) + f'?v={int(time.time() * 1000)}'
            return jsonify({
                'image_url': image_url,
                'mode': 'spots',
                'preset': preset_key,
                'stage_label': preset_spec.get('label', preset_key),
                'reference_step': int(preset_spec.get('reference_step', 0)),
                'download_name': f"figure_2_11_{preset_key}.png",
                'random_error_enabled': enable_random_error,
                'random_error_profile': random_error_params if enable_random_error else None,
                'stage_spec': {
                    'label': preset_spec.get('label', preset_key),
                    'reference_report': preset_spec.get('reference_report', ''),
                    'reference_step': preset_spec.get('reference_step', 0),
                    'reference_t': preset_spec.get('reference_t', 0.0),
                    'source_file': preset_spec.get('source_file', ''),
                },
                'applied_params_override': base_params,
            })
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
