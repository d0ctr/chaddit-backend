import os
from flask import json, request, Response, g
from functools import wraps
from ..models import TopicModel, ThreadModel, PostModel, ChatModel, UserModel, RoleModel, MessageModel
from ..schemas import TopicSchema, ThreadSchema, PostSchema, ChatSchema, UserSchema, RoleSchema, MessageSchema
from .constants import RoleId

def del_messages():
  for message in MessageModel.get_all():
    message.delete()

def del_chats():
  for chat in ChatModel.get_all():
    chat.delete()

def del_tags():
  for tag in TopicTagModel.get_all():
    tag.delete()

def del_threads():
  for thread in ThreadModel.get_all():
    thread.delete()

def del_topics():
  for topic in TopicModel.get_all():
    topic.delete()

def del_users():
  for user in UserModel.get_all():
    user.delete()

def del_roles():
  for role in RoleModel.get_all():
    role.delete()

def def_roles():
  if RoleModel.query.count() == 0:
    RoleModel({'role_id': 1, 'role_name' : 'ADMIN'}).\
      save()
    RoleModel({'role_id': 2, 'role_name' : 'MOD'}).\
      save()
    RoleModel({'role_id': 3, 'role_name' : 'USER'}).\
      save()
    


def add_admin():
  if UserModel.query.count() == 0:
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_pswd = os.getenv('ADMIN_PSWD')

    if not admin_email:
      admin_email = 'admin@chaddit.tk'
    
    if not admin_pswd:
      admin_pswd = 'admin'

    UserModel({'user_id': 1, 'role_id': 1,'user_name' : 'admin', 'user_email' : admin_email, 'user_pass' : admin_pswd, 'role_id': RoleId.ADMINISTRATOR}).\
      save()

def add_user():
  if UserModel.query.count() == 1:
    UserModel({'user_id': 2, 'role_id': 3,'user_name' : 'user', 'user_email' : 'user@chaddit.tk', 'user_pass' : 'user', 'role_id': RoleId.USER}).\
      save()

def add_topic():
  if TopicModel.query.count() == 0:
    TopicModel({'topic_id' : 1, 'topic_title': 'Welcome to chaddit', 'tags':[{'tag': 'info'}], 'author_id' : 1}).\
      save()

def add_thread():
  if ThreadModel.query.count() == 0:
    ThreadModel({'thread_id': 1, 'thread_title': 'Short information', 'author_id': 1, 'topic_id': 1}).\
      save()
def add_post():
  if PostModel.query.count() == 0:
    PostModel({'post_id': 1, 'body': 'We welcome you on Chaddit -- the first imagebaord with chat-roulette.\nBe welcome to create your first topic here and discuss your ideas with others.\nGithub: @vladislavzasyadko, @d0ctr, @neverovskii, @mishokU', 'author_id': 1, 'thread_id': 1}).\
      save()

def add_chat():
  if ChatModel.query.count() == 0:
    chat = ChatModel({'chat_id': 1})
    user = UserModel.get_by_id(1)
    user.chats.append(chat)
    user = UserModel.get_by_id(2)
    user.chats.append(chat)
    chat.update({'full': True})
    chat.save()

def add_messages():
  if MessageModel.query.count() == 0:
    MessageModel({'chat_id': 1, 'author_id': 1, 'message_id': 1, 'body': 'First message here'}).save()




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
          response = json.dumps({'error': 'Invalid post, access real one to continue.'}),
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