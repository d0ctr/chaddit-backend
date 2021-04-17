import datetime
from . import db

class MessageModel(db.Model):
  __tablename__ = 'messages'
  message_id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
  chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable = False)
  active = db.Column(db.Boolean, default = True)
  author = db.relationship('UserModel', back_populates = 'messages', uselist = False, lazy = True, cascade = 'all, delete') 
  chats = db.relationship('ChatModel', back_populates = 'messages', lazy = 'noload', cascade = 'all, delete')

  def __init__(self, data):
    self.body = data.get('body')
    self.author_id = data.get('author_id')
    self.chat_id = data.get('chat_id')
    self.image = data.get('image')
    self.active = True
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'author':
        continue
      if key == 'chats':
        continue
      setattr(self, key, item)
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all():
    return MessageModel.query.all()

  @staticmethod
  def get_by_chat(chat_id):
    return MessageModel.query.filter_by(chat_id = chat_id).all()

  @staticmethod
  def get_by_id(chat_id):
    return MessageModel.query.get(chat_id)

  def __repr__(self):
    return '<message_id {}, body {}, created_at {}, updated_at {}, author_id {}, chat_id {}, active {}>' \
      .format(self.message_id, self.body, self.created_at, self.updated_at, self.author_id, self.chat_id, self.active)

