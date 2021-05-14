import datetime
from . import db

class RoleModel(db.Model):
  __tablename__ = 'roles'
  role_id = db.Column(db.Integer, primary_key = True)
  role_name = db.Column(db.String)
  users = db.relationship('UserModel', back_populates = 'role', cascade = 'all, delete')

  def __init__(self, data):
    self.role_name = data.get('role_name')

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all():
    return RoleModel.query.all()

  @staticmethod
  def get(id):
    return RoleModel.query.get(id)

  def __repr__(self):
    return '<' + ', '.join('%s: {%s}' % item for item in vars(self).items()) + '>'
