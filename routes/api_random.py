"""Random error API route extracted from the main API module."""

from __future__ import annotations

import os
from importlib import import_module

from flask import jsonify, request, url_for


def register_random_routes(api):
    """Register the random-error endpoint on the shared API blueprint."""

    @api.route('/calculate_random', methods=['POST'])
    def calculate_random():
        """
        Generate mathematical texture with random error/noise injection.

        Expected JSON payload:
        {
            "K": float,              # Reaction constant (0.1 - 5.0)
            "t_max": float,          # Maximum simulation time
            "delta_t": float,        # Time step size
            "color1": string,        # Base color (hex format)
            "color2": string,        # Contrast color (hex format)
            "noise_target": string,  # 'A', 'B', or 'Both'
            "noise_type": string,    # 'initial' or 'dynamic'
            "noise_strength": float, # 0.001 - 0.05
            "noise_frequency": int   # 1 - 1000 (for dynamic noise)
        }

        Returns:
        {
            "image_url": string  # URL to generated texture image
        } or {"error": string}
        """
        try:
            api_module = import_module("routes.api")
            texture_service = api_module.texture_service
            validate_texture_params = api_module.validate_texture_params
            simulation_presets = getattr(api_module, "SIMULATION_PRESETS", {})

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            validation_result = validate_texture_params(data)
            if not validation_result['valid']:
                return jsonify({'error': validation_result['error']}), 400

            params = validation_result['params']

            noise_target = data.get('noise_target', 'Both')
            noise_type = data.get('noise_type', 'initial')
            noise_strength = float(data.get('noise_strength', 0.01))
            noise_frequency = int(data.get('noise_frequency', 10))
            explosion_density = float(data.get('explosion_density', 0.1))

            if noise_target not in ['A', 'B', 'Both']:
                return jsonify({'error': 'noise_target must be A, B, or Both'}), 400
            if noise_type not in ['initial', 'dynamic']:
                return jsonify({'error': 'noise_type must be initial or dynamic'}), 400
            if not (0.001 <= noise_strength <= 0.05):
                return jsonify({'error': 'noise_strength must be between 0.001 and 0.05'}), 400
            if not (1 <= noise_frequency <= 1000):
                return jsonify({'error': 'noise_frequency must be between 1 and 1000'}), 400
            if not (0.0 <= explosion_density <= 0.5):
                return jsonify({'error': 'explosion_density must be between 0.0 and 0.5'}), 400

            preset_key = (data.get('preset') or '').strip().lower()
            preset_params = simulation_presets.get(preset_key, {})

            image_path = texture_service.generate_random_error(
                K=params['K'],
                t_max=params['t_max'],
                delta_t=params['delta_t'],
                color1=params['color1'],
                color2=params['color2'],
                noise_target=noise_target,
                noise_type=noise_type,
                noise_strength=noise_strength,
                noise_frequency=noise_frequency,
                explosion_density=explosion_density,
                params_override=preset_params,
            )

            filename = os.path.basename(image_path)
            image_url = url_for('static', filename=f'images/{filename}', _external=True)
            return jsonify({'image_url': image_url})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
