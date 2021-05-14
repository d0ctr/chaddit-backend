import datetime
from . import db, hybrid_property, select, func, desc
from .post import PostModel


class ThreadModel(db.Model):
  __tablename__ = 'threads'
  thread_id = db.Column(db.Integer, primary_key = True)
  thread_title = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
  topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable = False)
  image = db.Column(db.Text)
  active = db.Column(db.Boolean, default = True)
  views = db.Column(db.Integer, default = 0)
  posts = db.relationship('PostModel', backref = 'threads',
                          primaryjoin = "and_(ThreadModel.thread_id==PostModel.thread_id, PostModel.root_post_id==None)",
                          lazy=True, cascade = 'all, delete')
  author = db.relationship('UserModel', back_populates = 'threads', uselist = False, lazy = True, cascade = 'all, delete')

  @hybrid_property
  def posts_count(self):
    return PostModel.query.filter_by(thread_id = self.thread_id).count()

  @posts_count.expression
  def posts_count(cls):
    return select([func.count(PostModel.post_id)]).\
            where(PostModel.thread_id == cls.thread_id)

  def __init__(self, data):
    self.thread_title = data.get('thread_title')
    self.author_id = data.get('author_id')
    self.image = data.get('image')
    self.active = True
    self.topic_id = data.get('topic_id')
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at
    self.views = 0

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'posts':
        continue
      if key == 'image':
        if item != None:
          item = item.encode()
      setattr(self, key, item)
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all(orderby='date', order='desc'):
    if orderby == 'date':
      if order == 'asc':
        return ThreadModel.query.order_by(ThreadModel.created_at)
      elif order == 'desc':
        return ThreadModel.query.order_by(desc(ThreadModel.created_at))
    elif orderby == 'alphabet':
      if order == 'asc':
        return ThreadModel.query.order_by(ThreadModel.thread_title)
      elif order == 'desc':
        return ThreadModel.query.order_by(desc(ThreadModel.thread_title))
    elif orderby == 'popularity':
      if order == 'asc':
        return ThreadModel.query.order_by(ThreadModel.views)
      elif order == 'desc':
        return ThreadModel.query.order_by(desc(ThreadModel.views))
    else:
      return ThreadModel.query.order_by(ThreadModel.created_at)

  @staticmethod
  def get_by_id(id):
    return ThreadModel.query.get(id)

  @staticmethod
  def get_by_topic_id(topic_id, orderby='date', order='desc'):
    if orderby == 'date':
      if order == 'asc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.created_at)
      elif order == 'desc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.created_at.desc())
    elif orderby == 'alphabet':
      if order == 'asc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.thread_title)
      elif order == 'desc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.thread_title.desc())
    elif orderby == 'popularity':
      if order == 'asc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.views)
      elif order == 'desc':
        return ThreadModel.query.filter_by(topic_id=topic_id).order_by(desc(ThreadModel.views))
    else:
      return ThreadModel.query.filter_by(topic_id=topic_id).order_by(ThreadModel.created_at)

  def __repr__(self):
    return '<' + ', '.join('%s: {%s}' % item for item in vars(self).items()) + '>'
