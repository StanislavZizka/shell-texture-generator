"""
API Routes - JSON endpoint handlers for texture generation

Handles all AJAX requests and returns JSON responses for the texture generator.
Provides endpoints for mathematical pattern generation algorithms.
"""
from flask import Blueprint, request, jsonify, url_for
from services.texture_generator import TextureGeneratorService
from utils.helpers import validate_texture_params

# Create Blueprint for API routes organization
api = Blueprint('api', __name__)

# Initialize texture generation service
texture_service = TextureGeneratorService()

@api.route('/calculate', methods=['POST'])
def calculate():
    """
    Generate mathematical texture based on reaction-diffusion parameters.
    
    Expected JSON payload:
    {
        "K": float,         # Reaction constant (0.1 - 5.0)
        "t_max": float,     # Maximum simulation time
        "delta_t": float,   # Time step size
        "color1": string,   # Base color (hex format)
        "color2": string    # Contrast color (hex format)
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
        
        # Generate texture using activator-inhibitor model
        image_path = texture_service.generate_activator_inhibitor(
            K=params['K'],
            t_max=params['t_max'],
            delta_t=params['delta_t'],
            color1=params['color1'],
            color2=params['color2']
        )
        
        # Return generated image URL for client consumption
        image_url = url_for('static', filename='images/activator_inhibitor_texture.png', _external=True)
        return jsonify({'image_url': image_url})
    
    except Exception as e:
        # Log error and return user-friendly message
        return jsonify({'error': str(e)}), 500