from . import db

class TopicTagModel(db.Model):
  __tablename__ = 'topic_tag'
  tag_id = db.Column(db.Integer, primary_key = True)
  topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable = False)
  tag = db.Column(db.String, nullable = False)

  def __init__(self, data):
    self.topic_id = data.get('topic_id')
    self.tag = data.get('tag')

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    db.session.commit()
  
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_by_id(id):
    return TopicTagModel.query.get(id)
  
  @staticmethod
  def get_by_tag(tag):
    return TopicTagModel.query.filter_by(tag = tag)
  
  def __repr__(self):
    return '<tag_id {}, topic_id {}, tag {}>' \
      .format(self.tag_id, self.topic_id, self.tag)