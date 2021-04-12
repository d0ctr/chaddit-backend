import os
import eventlet
from flask_migrate import Migrate
from src.app import create_app
from src.app import socketio
from src.models import db
from dotenv import load_dotenv

eventlet.monkey_patch()

load_dotenv(override=False)

env_name = os.getenv('FLASK_ENV')

app = create_app(env_name)

with open('redirection_rules.txt', 'w') as redirection_rules:
    redirection_rules.write(str(app.url_map))


if __name__ == "__main__":
  socketio.run(app, host='0.0.0.0')