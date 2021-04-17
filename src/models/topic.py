import datetime
from . import db, hybrid_property, select, func, desc
from .topictag import TopicTagModel
from .thread import ThreadModel

class TopicModel(db.Model):
  __tablename__ = 'topics'
  topic_id = db.Column(db.Integer, primary_key = True)
  topic_title = db.Column(db.Text)
  created_at = db.Column(db.DateTime)
  updated_at = db.Column(db.DateTime)
  author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
  image = db.Column(db.Text)
  active = db.Column(db.Boolean, default = True)
  chats = db.relationship('ChatModel', backref = 'topics', lazy = 'noload', cascade = 'all, delete')
  threads = db.relationship('ThreadModel', backref = 'topics', lazy = 'dynamic', cascade = 'all, delete')
  tags = db.relationship('TopicTagModel', backref = 'topics', lazy = True, cascade = 'all, delete')
  author = db.relationship('UserModel', back_populates = 'topics', uselist = False, lazy = True, cascade = 'all, delete')
  
  @hybrid_property
  def threads_count(self):
    return self.threads.count()

  @threads_count.expression
  def threads_count(cls):
    return select([func.count(ThreadModel.thread_id)]).\
            where(ThreadModel.topic_id == cls.topic_id)

  def __init__(self, data):
    self.topic_title = data.get('topic_title')
    self.author_id = data.get('author_id')
    self.image = data.get('image')
    self.active = True
    self.created_at = datetime.datetime.utcnow()
    self.updated_at = self.created_at
    self.tags.extend([TopicTagModel(tag) for tag in data.get('tags')])

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):

    for key, item in data.items():
      if key == 'tags':
        for tag in item:
          if tag.get('tag_id'):
            if tag.get('tag') == '':
              old_tag = TopicTagModel.get_by_id(tag.get('tag_id'))
              old_tag.delete()
            else:
              old_tag = TopicTagModel.get_by_id(tag.get('tag_id'))
              old_tag.update(tag)
          else:
            new_tag = TopicTagModel(tag)
            new_tag.topic_id = self.topic_id
            new_tag.save()
        continue


      setattr(self, key, item)
      if key == 'image':
        if item != None:
          item = item.encode()
    self.updated_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all(orderby = 'date', order = 'desc'):
    if orderby == 'date':
      if order == 'asc':
        return TopicModel.query.order_by(TopicModel.created_at)
      elif order == 'desc':
        return TopicModel.query.order_by(TopicModel.created_at.desc())
    elif orderby == 'alphabet':
      if order == 'asc':
        return TopicModel.query.order_by(TopicModel.topic_title)
      elif order == 'desc':
        return TopicModel.query.order_by(TopicModel.topic_title.desc())
    elif orderby == 'popularity':
      if order == 'asc':
        return TopicModel.query.order_by(TopicModel.threads_count)
      elif order == 'desc':
        return TopicModel.query.order_by(desc(TopicModel.threads_count))
    else:
      return TopicModel.query.order_by(TopicModel.created_at)

  @staticmethod
  def get_by_ids(ids):
    res = []
    for id in ids:
      res.append(TopicModel.get_by_id(id))
    return res

  @staticmethod
  def get_by_id(id):
    return TopicModel.query.get(id)

  def __repr__(self):
    return '<topic_id {}, topic_title {}, created_at {}, updated_at {}, author_id {}, active {}>' \
      .format(self.topic_id, self.topic_title, self.created_at, self.updated_at, self.author_id, self.active)
