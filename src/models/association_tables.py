from . import db

# user to chat

user_to_chat = db.Table('user_to_chat', db.Model.metadata,
  db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
  db.Column('chat_id', db.Integer, db.ForeignKey('chats.chat_id'))
)