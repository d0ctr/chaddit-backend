import os
import eventlet
from src.app import create_app
from src.app import socketio
from dotenv import load_dotenv

eventlet.monkey_patch()

load_dotenv(override=False)

env_name = os.getenv('FLASK_ENV')

app = create_app(env_name)

with open('redirection_rules.txt', 'w') as redirection_rules:
    [redirection_rules.write(str(rule.methods) + '\t==>\t' + str(rule) + '\n') for rule in app.url_map.iter_rules()]


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
