"""
Shell Texture Generator - Diploma Thesis Project

A web application that generates mathematical textures for seashells using 
reaction-diffusion algorithms. This tool helps researchers and designers 
visualize how natural patterns form on shell surfaces.

Author: Stanislav
Year: 2024
"""

# Import Flask - the web framework that makes our app work
from flask import Flask

# Create our web application
app = Flask(__name__)

# Define the main page route - this is what users see when they visit our website
@app.route('/')
def home():
    """
    Main page of the application.
    Shows a welcome message and basic information about the texture generator.
    """
    return """
    <html>
        <head>
            <title>Shell Texture Generator</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: #f5f5f5; 
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #2c3e50; }
                p { line-height: 1.6; color: #555; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🐚 Shell Texture Generator</h1>
                <p><strong>Welcome to the Shell Texture Generator!</strong></p>
                <p>This application uses mathematical algorithms to generate 
                   realistic textures that mimic the natural patterns found 
                   on seashells.</p>
                <p>Perfect for research, design, and understanding how 
                   nature creates beautiful patterns through simple rules.</p>
                <p><em>More features coming soon...</em></p>
            </div>
        </body>
    </html>
    """

# This runs the web server when we start the application
if __name__ == '__main__':
    # Start the development server
    # debug=True means we can see errors clearly during development
    app.run(debug=True, host='0.0.0.0', port=5000)