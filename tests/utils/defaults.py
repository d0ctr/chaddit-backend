import os
from src.models import TopicModel, ThreadModel, PostModel, ChatModel, UserModel, RoleModel, MessageModel
from src.shared.constants import RoleId

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
    TopicModel({'topic_id' : 1, 'topic_title': 'Test_topic_1', 'tags':[{'tag': 'test'}], 'author_id' : 1}).\
      save()

def add_thread():
  if ThreadModel.query.count() == 0:
    ThreadModel({'thread_id': 1, 'thread_title': 'Test_thread_1', 'author_id': 1, 'topic_id': 1}).\
      save()
def add_post():
  if PostModel.query.count() == 0:
    PostModel({'post_id': 1, 'body': 'Test_post_1', 'author_id': 1, 'thread_id': 1}).\
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
    MessageModel({'chat_id': 1, 'author_id': 1, 'message_id': 1, 'body': 'test_message_1'}).save()
