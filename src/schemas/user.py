from . import fields, Schema, EXCLUDE
from . import topic, thread, message, post, chat

class UserSchema(Schema):
  user_id = fields.Integer(dump_only = True)
  user_name = fields.Str()
  user_tag = fields.Str(dump_only = True)
  user_email = fields.Email()
  user_pass = fields.Str(load_only = True)
  created_at = fields.DateTime(dump_only = True)
  updated_at = fields.DateTime(dump_only = True)
  role_id = fields.Integer()
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  role = fields.Nested('RoleSchema', dump_only = True)

  class Meta():
    unknown = EXCLUDE