from . import fields, Schema
from . import user

class RoleSchema(Schema):
  role_id = fields.Int()
  role_name = fields.Str()