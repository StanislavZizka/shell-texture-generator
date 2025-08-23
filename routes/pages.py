"""
Page Routes - HTML Template Rendering

In the original November prototype, all routes were mixed together in app.py.
Now we're separating concerns properly - this file only handles pages that
show HTML to users (not API endpoints that return data).

This follows Flask Blueprint pattern for better code organization.
"""
from flask import Blueprint, render_template, send_from_directory

# Create a Blueprint - think of it as a mini-app for organizing related routes
# The 'pages' name helps Flask organize our URL routing
pages = Blueprint('pages', __name__)

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

@pages.route('/activator_inhibitor')
def activator_inhibitor():
    """
    Activator-Inhibitor model page route.
    
    Renders the texture generation interface for reaction-diffusion
    mathematical models. Users can adjust parameters and generate patterns.
    
    Returns:
        Rendered HTML template for the activator-inhibitor interface
    """
    return render_template('activator_inhibitor.html')

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
    return send_from_directory('assets', filename)