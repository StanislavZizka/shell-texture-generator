"""Localized disturbance API route extracted from the main API module."""

from __future__ import annotations

import os

from flask import jsonify, request, url_for


def register_localized_routes(api, *, texture_service, validate_texture_params, simulation_presets):
    """Register the localized disturbance endpoint on the shared API blueprint."""

    @api.route('/calculate_localized', methods=['POST'])
    def calculate_localized():
        """
        Generate texture with localized pattern stability breakdown.

        Expected JSON payload:
        {
            "K": float,
            "t_max": float,
            "delta_t": float,
            "color1": string,
            "color2": string,
            "intensity": float,          # 0.03 - 0.07
            "block_size": int,           # 20 - 40
            "target": string,            # 'activator', 'inhibitor', 'both', 'parameters'
            "variation_percent": float,  # 10 - 50
            "noise_type_disturbance": string  # 'perlin', 'block', 'smooth_block'
        }

        Returns:
        {
            "image_url": string
        } or {"error": string}
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            validation_result = validate_texture_params(data)
            if not validation_result['valid']:
                return jsonify({'error': validation_result['error']}), 400

            params = validation_result['params']

            intensity = float(data.get('intensity', 0.05))
            block_size = int(data.get('block_size', 30))
            target = data.get('target', 'both')
            variation_percent = float(data.get('variation_percent', 30.0))
            noise_type_disturbance = data.get('noise_type_disturbance', 'perlin')

            if not (0.03 <= intensity <= 0.07):
                return jsonify({'error': 'intensity must be between 0.03 and 0.07'}), 400
            if not (20 <= block_size <= 40):
                return jsonify({'error': 'block_size must be between 20 and 40'}), 400
            if target not in ['activator', 'inhibitor', 'both', 'parameters']:
                return jsonify({'error': 'target must be activator, inhibitor, both, or parameters'}), 400
            if not (10.0 <= variation_percent <= 50.0):
                return jsonify({'error': 'variation_percent must be between 10 and 50'}), 400
            if noise_type_disturbance not in ['perlin', 'block', 'smooth_block']:
                return jsonify({'error': 'noise_type_disturbance must be perlin, block, or smooth_block'}), 400

            preset_key = (data.get('preset') or '').strip().lower()
            preset_params = simulation_presets.get(preset_key, {})

            image_path = texture_service.generate_localized_disturbance(
                K=params['K'],
                t_max=params['t_max'],
                delta_t=params['delta_t'],
                color1=params['color1'],
                color2=params['color2'],
                intensity=intensity,
                block_size=block_size,
                target=target,
                variation_percent=variation_percent,
                noise_type_disturbance=noise_type_disturbance,
                params_override=preset_params,
            )

            filename = os.path.basename(image_path)
            image_url = url_for('static', filename=f'images/{filename}', _external=True)
            return jsonify({'image_url': image_url})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
