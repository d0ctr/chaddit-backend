from . import fields, Schema, EXCLUDE, role

class UserSchema(Schema):
  user_id = fields.Integer()
  user_name = fields.Str()
  user_tag = fields.Str()
  user_email = fields.Email()
  user_pass = fields.Str()
  created_at = fields.DateTime()
  updated_at = fields.DateTime()
  role_id = fields.Integer()
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  role = fields.Nested(role.RoleSchema)

  class Meta():
    unknown = EXCLUDE