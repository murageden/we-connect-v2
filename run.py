"""/run.py."""
import os

# local import
from api import create_app


config_name = os.getenv('APP_CONFIGURATION')
app = create_app(config_name)


if __name__ == '__main__':
    app.run()
