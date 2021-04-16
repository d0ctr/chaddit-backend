from . import fields, Schema, EXCLUDE, user

class ChatSchema(Schema):
  chat_id = fields.Int(dump_only = True)
  created_at = fields.DateTime(dump_only = True)
  updated_at = fields.DateTime(dump_only = True)
  topic_id = fields.Integer()
  active = fields.Boolean()
  full = fields.Boolean()
  participants = fields.Nested(user.UserSchema, dump_only = True, many = True)
  
  class Meta:
    unknown = EXCLUDE