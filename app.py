"""
Shell Texture Generator - Mathematical Pattern Generation

Web application for generating mathematical textures using reaction-diffusion
algorithms. Creates natural-looking patterns for shell surface visualization.
"""
import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for serverless deployment

from flask import Flask
from config import config
from routes.pages import pages
from routes.api import api

def create_app(config_name=None):
    """
    Flask application factory pattern.
    Enables easy testing and deployment in different environments.
    
    Args:
        config_name: Configuration environment ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Determine configuration environment
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Create Flask application instance
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints for modular routing
    app.register_blueprint(pages)
    app.register_blueprint(api)
    
    # Register custom error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register custom error handlers for better user experience."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad request'}, 400

# Create application instance
app = create_app()

# For serverless deployment compatibility
application = app

if __name__ == '__main__':
    # Development server configuration
    app.run(debug=True, host='0.0.0.0', port=5000)