from . import fields, Schema, EXCLUDE, user

class ChatSchema(Schema):
  chat_id = fields.Int()
  created_at = fields.DateTime()
  updated_at = fields.DateTime()
  topic_id = fields.Integer()
  active = fields.Boolean()
  full = fields.Boolean()
  participants = fields.Nested(user.UserSchema, many = True)
  
  class Meta:
    unknown = EXCLUDE