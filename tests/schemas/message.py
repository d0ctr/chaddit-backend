from . import fields, Schema, EXCLUDE

class MessageSchema(Schema):
  message_id = fields.Int()
  body = fields.Str()
  created_at = fields.DateTime()
  updated_at =  fields.DateTime()
  author_id = fields.Int()
  chat_id = fields.Int()
  active = fields.Boolean()

  class Meta:
    unknown = EXCLUDE