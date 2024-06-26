"""
   This module responsible for all initial configurations
"""
import os
from flask import Flask
from flasgger import Swagger
import yaml
from cache import cache

app = Flask(__name__)

# Configure cache
app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_DIR"] = "./cache"

cache.init_app(app)

if __name__ == '__main__':
    from api import api_bp
    # Load and parse the external YAML file for Swagger
    template_file_path = os.path.join(os.getcwd(), 'swagger.yml')
    with open(template_file_path, 'r', encoding='utf-8') as f:
        template = yaml.safe_load(f.read())

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    Swagger(app, template=template, config=swagger_config)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.run(debug=True, port=3000)
