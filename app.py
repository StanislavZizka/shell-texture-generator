"""
Shell Texture Generator - Diploma Thesis Project

Web application for generating mathematical textures using reaction-diffusion
algorithms. Simulates the formation of natural patterns on shell surfaces.

Author: Stanislav Žižka
Year: 2024/2025
"""

# Import Flask - web framework for Python
from flask import Flask
from config import config
from routes.pages import pages

def create_app(config_name=None):
    """
    Factory pattern for creating Flask application.
    Enables easy testing and deployment in different environments.
    
    Args:
        config_name: Configuration type ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    # Determine configuration type
    if config_name is None:
        config_name = 'development'
    
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints for route organization
    app.register_blueprint(pages)
    
    return app

# Create application instance
app = create_app()

# Run application for development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)