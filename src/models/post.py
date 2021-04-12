import datetime
from . import db

class PostModel(db.Model):
  __tablename__ = 'posts'
  post_id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
  image = db.Column(db.LargeBinary)
  thread_id = db.Column(db.Integer, db.ForeignKey('threads.thread_id'), nullable = False)
  root_post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
  active = db.Column(db.Boolean, default = True)
  responses = db.relationship('PostModel', lazy = True, cascade = 'all, delete')
  author = db.relationship('UserModel', back_populates = 'posts', uselist = False, lazy = True)

  def __init__(self, data):
    self.body = data.get('body')
    self.author_id = data.get('author_id')
    self.image = data.get('image')
    self.active = True
    self.thread_id = data.get('thread_id')
    self.root_post_id = data.get('root_post_id')
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all():
    return PostModel.query.all()

  @staticmethod
  def get_by_thread_id(thread_id):
    return PostModel.query.filter_by(thread_id = thread_id)

  @staticmethod
  def get_by_root_post_id(root_post_id):
    return PostModel.query.filter_by(root_post_id = root_post_id)

  @staticmethod
  def get_by_id(id):
    return PostModel.query.get(id)

  def __repr__(self):
    return '<post_id {}, body {}, created_at {}, updated_at {}, author_id {}, thread_id {}, root_post_id {}, active {}>' \
      .format(self.post_id, self.body, self.created_at, self.updated_at, self.author_id, self.thread_id, self.root_post_id, self.active)