"""
Generátor Textur pro Mušle - Diplomová práce

Webová aplikace pro generování matematických textur pomocí reakčně-difuzních
algoritmů. Simuluje vznik přírodních vzorů na površích mušlí.

Autor: Stanislav Žižka
Rok: 2024/2025
"""

# Import Flask - webový framework pro Python
from flask import Flask
from config import config
from routes.pages import pages

def create_app(config_name=None):
    """
    Factory pattern pro vytvoření Flask aplikace.
    Umožňuje snadné testování a deployment v různých prostředích.
    
    Args:
        config_name: Typ konfigurace ('development', 'production', 'testing')
        
    Returns:
        Flask: Nakonfigurovaná Flask aplikace
    """
    # Určení typu konfigurace
    if config_name is None:
        config_name = 'development'
    
    # Vytvoření Flask aplikace
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Registrace blueprintů pro organizaci routů
    app.register_blueprint(pages)
    
    return app

# Vytvoření instance aplikace
app = create_app()

# Spuštění aplikace pro development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)