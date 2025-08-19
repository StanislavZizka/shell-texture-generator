# Shell Texture Generator

Web application for generating mathematical textures using reaction-diffusion algorithms. The project simulates the formation of natural patterns on shell surfaces.

## About the Project

This project explores how complex patterns in nature arise through simple mathematical rules. The application implements activator-inhibitor models to create realistic textures that mimic patterns found on real shells.

## Technologies

- **Flask** - Python web framework
- **NumPy** - mathematical computations and array operations
- **Matplotlib** - texture generation and image saving
- **HTML/CSS/JavaScript** - modern web interface

## Features

- Interactive texture generation using mathematical models
- Adjustable parameters for different pattern types
- Real-time result visualization
- Export generated textures
- Multi-language interface (Czech/English)

## Project Structure

```
shell-texture-generator/
├── app.py                 # Main Flask application
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
├── routes/              # URL routes
│   ├── __init__.py
│   ├── pages.py         # HTML pages
│   └── api.py           # API endpoints
├── services/            # Business logic
│   ├── __init__.py
│   └── texture_generator.py
├── utils/               # Helper functions
│   ├── __init__.py
│   └── helpers.py
├── templates/           # HTML templates
├── static/             # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── assets/             # 3D shell models
└── models/             # Data models
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser at: http://localhost:5000

## Development

The project is structured for easy maintenance and expansion:

- **Modularity** - each functionality has its own module
- **Separation** - HTML, CSS and JavaScript are separated
- **Configuration** - all settings centralized in config.py
- **Documentation** - code comments explain complex parts

## Author

Stanislav Žižka  
Diploma Thesis • 2024/2025