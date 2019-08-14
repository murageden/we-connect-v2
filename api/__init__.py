from flask_sqlalchemy import SQLAlchemy

from flask import Flask
from flask_cors import CORS

from api.instance.config import app_config

db = SQLAlchemy()

def create_app(config_name):
    """Configure and creates the app."""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app