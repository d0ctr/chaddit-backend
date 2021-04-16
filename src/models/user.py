import datetime
from . import db, bcrypt
from .association_tables import user_to_chat
from ..shared.constants import RoleId
import random

class UserModel(db.Model):
  __tablename__ = 'users'
  user_id = db.Column(db.Integer, primary_key = True)
  user_name = db.Column(db.Text)
  user_tag = db.Column(db.String(4))
  user_email = db.Column(db.Text, unique = True)
  user_pass = db.Column(db.String)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
  avatar = db.Column(db.Text)
  active = db.Column(db.Boolean, default = True)
  role = db.relationship('RoleModel', back_populates = 'users')
  topics = db.relationship('TopicModel', back_populates = 'author')
  threads = db.relationship('ThreadModel', back_populates = 'author')
  messages = db.relationship('MessageModel', back_populates = 'author', lazy = 'noload')
  posts = db.relationship('PostModel', back_populates = 'author', lazy = 'noload')
  chats = db.relationship('ChatModel', back_populates = 'participants', secondary = user_to_chat)

  def __init__(self, data):
    self.user_name = data.get('user_name')
    self.user_email = data.get('user_email')
    self.user_pass = self.__generate_hash(data.get('user_pass'))
    self.user_tag = self.__generate_tag(self.user_name)
    self.role_id = data.get('role_id') if data.get('role_id') else RoleId.USER
    self.active = True
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'user_pass':
        item = self.__generate_hash(item)

      if key == 'user_email':
        if item == '':
          continue
      setattr(self, key, item)
      if key == 'avatar':
        if item != None:
          item = item.encode()
      setattr(self, key, item)
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all():
    return UserModel.query.all()

  @staticmethod
  def get_by_id(id):
    return UserModel.query.get(id)

  @staticmethod
  def get_by_email(email):
    return UserModel.query.filter_by(user_email=email).first()

  def __repr__(self):
    return '<user_id {}, user_name {}, user_tag {}, user_email {}, created_at {}, updated_at {}, role_id {}, active {}>' \
      .format(self.user_id, self.user_name, self.user_tag, self.user_email, self.created_at, self.updated_at, self.role_id, self.active)

  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds = 10).decode('utf-8')

  def check_hash(self, password):
    return bcrypt.check_password_hash(self.user_pass, password)

  def __generate_tag(self, name):
    tags = UserModel.query.filter_by(user_name = name).with_entities(UserModel.user_tag).all()
    new_tag = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
    while tags.count(new_tag) > 1:
      new_tag = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
    return new_tag



