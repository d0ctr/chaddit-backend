from flask import Flask, g, render_template, request
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from .socketio import socketio
from .config import app_config
from .models import db, bcrypt
from .shared.utils import def_roles, add_admin, add_chat, add_messages, add_thread, add_topic, del_messages, del_chats, del_tags, del_threads, del_topics, del_users, del_roles

import time
import os

from .views.user import user_api as user_blueprint, register
from .views.topic import topic_api as topic_blueprint
from .views.thread import thread_api as thread_blueprint
from .views.post import post_api as post_blueprint
from .views.chat import chat_api as chat_blueprint
from .search.search import search_api as search_blueprint
from .views.message import message_api as message_blueprint


def create_app(env_name):

  app = Flask(__name__)
  migrate = Migrate()
  app.config.from_object(app_config[env_name])
  bcrypt.init_app(app)
  db.init_app(app)
  migrate.init_app(app, db, directory=os.getenv('MIGRATIONS_DIR'))
  socketio.init_app(app, cors_allowed_origins='*')
  CORS(app)

  app.register_blueprint(search_blueprint, url_prefix='/api/chaddit/c/')
  app.register_blueprint(user_blueprint, url_prefix='/api/chaddit/c/')
  app.register_blueprint(topic_blueprint, url_prefix='/api/chaddit/c/')
  app.register_blueprint(thread_blueprint, url_prefix='/api/chaddit/c/')
  app.register_blueprint(post_blueprint, url_prefix='/api/chaddit/c/')
  app.register_blueprint(chat_blueprint, url_prefix = '/api/chaddit/c/')
  app.register_blueprint(message_blueprint, url_prefix = '/api/chaddit/c/')

  @app.route('/api')
  def index():
    return render_template('index.html', key = app.config['SQLALCHEMY_DATABASE_URI'])

  @app.before_request
  def before_request():
    g.start = time.time()
    g.elapsed_time = lambda: '%.5fs' % (time.time() - g.start)

  @app.cli.command('check_initial_data')
  def check_initial_data():
    def_roles()
    add_admin()
    add_topic()
    add_thread()
    add_chat()
    add_messages()
  
  @app.cli.command('clear_data')
  def clear_data():
    db.drop_all()
    # del_messages()
    # del_chats()
    # del_tags()
    # del_threads()
    # del_topics()
    # del_users()
    # del_roles()

  return app
