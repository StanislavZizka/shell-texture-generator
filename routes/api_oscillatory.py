"""Oscillatory waves API route extracted from the main API module."""

from __future__ import annotations

import os

from flask import jsonify, request, url_for


def register_oscillatory_routes(api, *, static_dir):
    """Register the oscillatory waves endpoint on the shared API blueprint."""

    @api.route('/calculate_oscillatory_waves', methods=['POST'])
    def calculate_oscillatory_waves():
        """
        Calculate oscillatory waves using exact analytical solution from vypocet.txt.

        This endpoint implements the Riccati ODE solution step-by-step following
        the mathematical derivation in vypocet.txt (SOURCE OF TRUTH).
        """
        try:
            from services.oscillatory_waves import simulate_oscillatory_waves

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            params = {
                's': float(data.get('s', 0.11)),
                's_b': float(data.get('s_b', 1.0)),
                'b_0': float(data.get('b_0', 1.0)),
                'r_a': float(data.get('r_a', 0.10)),
                'b_a': float(data.get('b_a', 0.01)),
                'a_0': float(data.get('a_0', 0.5)),
                't_max': float(data.get('t_max', 100.0)),
                'dt': float(data.get('dt', 0.5))
            }

            # Validate ranges
            if not (0.01 <= params['s'] <= 2.0):
                return jsonify({'error': 's must be between 0.01 and 2.0'}), 400
            if not (0.01 <= params['r_a'] <= 3.0):
                return jsonify({'error': 'r_a must be between 0.01 and 3.0'}), 400

            # Run simulation (follows vypocet.txt exactly)
            result = simulate_oscillatory_waves(params)

            # Move verification file to static directory
            import shutil
            verification_file = result['verification_file']
            static_verification = os.path.join(static_dir, 'vypocet_output.txt')
            shutil.copy(verification_file, static_verification)

            verification_url = url_for('static', filename='vypocet_output.txt', _external=True)

            return jsonify({
                't_values': result['t_values'],
                'a_values': result['a_values'],
                'equilibrium_info': result['equilibrium_info'],
                'verification_url': verification_url
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
