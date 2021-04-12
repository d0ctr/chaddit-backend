from . import fields, Schema, EXCLUDE

class ThreadSchema(Schema):
  thread_id = fields.Int(dump_only = True)
  thread_title = fields.String()
  created_at = fields.DateTime(dump_only = True)
  updated_at = fields.DateTime(dump_only = True)
  author_id = fields.Int()
  image = fields.Raw(allow_none=True)
  active = fields.Bool()
  topic_id = fields.Int()
  posts = fields.Nested('PostSchema', many = True)
  author = fields.Nested('UserSchema', dump_only = True)
  posts_count = fields.Int(dump_only = True)
  views = fields.Int(dump_only = True)

  class Meta:
    unknown = EXCLUDE