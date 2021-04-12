import os
from flask import json, request, Response, g
from functools import wraps
from ..models import TopicModel, ThreadModel, PostModel, ChatModel, UserModel, RoleModel
from ..schemas import TopicSchema, ThreadSchema, PostSchema, ChatSchema, UserSchema, RoleSchema

def def_roles():
  if RoleModel.query.count() == 0:
    RoleModel(\
      RoleSchema().\
        load({'role_name' : 'ADMIN'})).\
          save()
    RoleModel(\
      RoleSchema().\
        load({'role_name' : 'MOD'})).\
          save()
    RoleModel(\
      RoleSchema().\
        load({'role_name' : 'USER'})).\
          save()
    


def add_admin():
  if UserModel.query.count() == 0:
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_pswd = os.getenv('ADMIN_PSWD')

    if not admin_email:
      admin_email = 'admin@chaddit.tk'
    
    if not admin_pswd:
      admin_pswd = 'admin'

    UserModel(\
      UserSchema().\
        load({'user_name' : 'admin', 'user_email' : admin_email, 'user_pass' : admin_pswd})).\
          save()



class CurrentWorkspace():
  @staticmethod
  def topic_required(func):
    @wraps(func)
    def topic_accessor(*args, **kwargs):
      if 'topic_id' not in request.headers:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Cannot access without being in topic, open or create one.'}),
          status = 400 
        )
      topic_id = request.headers.get('topic_id')

      topic = TopicModel.get_by_id(topic_id)
      if not topic:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Invalid topic, access real one to continue.'}),
          status = 400
        )
      
      g.topic = TopicSchema().dump(topic)

      return func(*args, **kwargs)
    return topic_accessor

  @staticmethod
  def thread_required(func):
    @wraps(func)
    def thread_accessor(*args, **kwargs):
      if 'thread_id' not in request.headers:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Cannot access without being in thread, open or create one.'}),
          status = 400 
        )
      thread_id = request.headers.get('thread_id')

      thread = ThreadModel.get_by_id(thread_id)
      if not thread:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Invalid thread, access real one to continue.'}),
          status = 400
        )
      
      g.thread = ThreadSchema().dump(thread)

      return func(*args, **kwargs)
    return thread_accessor

  @staticmethod
  def post_required(func):
    @wraps(func)
    def post_accessor(*args, **kwargs):
      if 'post_id' not in request.headers:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Reply must have a root, choose or create one.'}),
          status = 400 
        )
      post_id = request.headers.get('post_id')

      post = PostModel.get_by_id(post_id)
      if not post:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Invalid thread, access real one to continue.'}),
          status = 400
        )
      
      g.post = PostSchema().dump(post)

      return func(*args, **kwargs)
    return post_accessor

  @staticmethod
  def chat_required(func):
    @wraps(func)
    def chat_accessor(*args, **kwargs):
      if 'chat_id' not in request.headers:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Message must be in chat, choose or create one.'}),
          status = 400 
        )
      chat_id = request.headers.get('chat_id')

      chat = ChatModel.get_by_id(chat_id)
      if not chat:
        return Response(
          mimetype ='application/json',
          response = json.dumps({'error': 'Invalid chat, access real one to continue.'}),
          status = 400
        )
      
      g.chat = ChatSchema().dump(chat)

      return func(*args, **kwargs)
    return chat_accessor