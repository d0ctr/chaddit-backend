import datetime
import random
from . import db, hybrid_property, select, func
from .association_tables import user_to_chat
from .user import UserModel

from sqlalchemy import func

class ChatModel(db.Model):
  __tablename__ = 'chats'
  chat_id = db.Column(db.Integer, primary_key = True)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable = True)
  active = db.Column(db.Boolean, default = True)
  full = db.Column(db.Boolean, default = False)
  messages = db.relationship('MessageModel', back_populates = 'chats', lazy = 'noload')
  participants = db.relationship('UserModel', back_populates = 'chats', secondary = user_to_chat, lazy = 'dynamic', cascade = 'all, delete')

  def __init__(self, data):
    self.body = data.get('body')
    self.active = True
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at
    self.topic_id = data.get('topic_id')
    self.full = False

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'messages':
        continue
      if key == 'participants':
        continue
      setattr(self, key, item)
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all():
    return ChatModel.query.all()

  @staticmethod
  def get_by_id(chat_id):
    return ChatModel.query.get(chat_id)

  @staticmethod
  def get_by_user(user_id):
    return ChatModel.query.join(user_to_chat).join(UserModel).filter(user_to_chat.c.user_id == user_id).all()
  
  @staticmethod
  def get_vacant_chat(user_id, topic_id = None):
    chats = ChatModel.query.filter_by(full = False)
    if not topic_id:
      chats.filter_by(topic_id = topic_id)
    
    chats = [chat for chat in chats.all() if chat.participants[0].user_id != user_id]
    if len(chats) == 0:
      return None
    else:
      chat = random.choice(chats)
      print(chat)
      return chat

  def __repr__(self):
    return '<chat_id {}, created_at {}, updated_at {}, topic_id {}, active {}, full {}>' \
      .format(self.chat_id, self.created_at, self.updated_at, self.topic_id, self.active, self.full)

