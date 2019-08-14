"""/run.py."""
import os
from flask import Flask
from flask_cors import CORS

# local import
from .instance.config import app_config


def create_app(config_name):
    """Configure and creates the app."""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app


config_name = os.getenv('APP_CONFIGURATION')
app = create_app(config_name)


if __name__ == '__main__':
    app.run()
