from . import fields, Schema, EXCLUDE, user

class PostSchema(Schema):
  post_id = fields.Int()
  body = fields.Str()
  created_at = fields.DateTime()
  updated_at = fields.DateTime()
  author_id = fields.Int()
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  thread_id = fields.Int()
  root_post_id = fields.Int(allow_none = True)
  responses = fields.Nested('src.schemas.post.PostSchema', many = True)
  author = fields.Nested(user.UserSchema)
  
  class Meta():
    unknown = EXCLUDE