from . import fields, Schema, EXCLUDE, user

class PostSchema(Schema):
  post_id = fields.Int(dump_only = True)
  body = fields.Str()
  created_at = fields.DateTime(dump_only = True)
  updated_at = fields.DateTime(dump_only = True)
  author_id = fields.Int()
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  thread_id = fields.Int()
  root_post_id = fields.Int(allow_none = True)
  responses = fields.Nested('src.schemas.post.PostSchema', many = True)
  author = fields.Nested(user.UserSchema, dump_only = True)
  
  class Meta():
    unknown = EXCLUDE