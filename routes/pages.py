"""
Page Routes - HTML Template Rendering

In the original November prototype, all routes were mixed together in app.py.
Now we're separating concerns properly - this file only handles pages that
show HTML to users (not API endpoints that return data).

This follows Flask Blueprint pattern for better code organization.
"""
from flask import Blueprint, render_template

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