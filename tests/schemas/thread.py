from . import fields, Schema, EXCLUDE, post, user

class ThreadSchema(Schema):
  thread_id = fields.Int()
  thread_title = fields.String()
  created_at = fields.DateTime()
  updated_at = fields.DateTime()
  author_id = fields.Int()
  image = fields.Raw()
  active = fields.Bool()
  topic_id = fields.Int()
  posts = fields.Nested(post.PostSchema, many = True)
  author = fields.Nested(user.UserSchema)
  posts_count = fields.Int()
  views = fields.Int()

  class Meta:
    unknown = EXCLUDE