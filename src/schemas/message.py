from . import fields, Schema, EXCLUDE

class MessageSchema(Schema):
  message_id = fields.Int(dump_only = True)
  body = fields.Str()
  created_at = fields.DateTime(dump_only = True)
  updated_at =  fields.DateTime(dump_only = True)
  author_id = fields.Int()
  chat_id = fields.Int()
  active = fields.Boolean()

  class Meta:
    unknown = EXCLUDE