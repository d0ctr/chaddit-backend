from . import fields, Schema, EXCLUDE, topictag, user

class TopicSchema(Schema):
  topic_id = fields.Int()
  topic_title = fields.Str()
  created_at = fields.DateTime()
  updated_at = fields.DateTime()
  author_id = fields.Int()
  tags = fields.Nested(topictag.TopicTagSchema, many = True, allow_none = False)
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  author = fields.Nested(user.UserSchema)
  threads_count = fields.Int()

  class Meta():
    unknown = EXCLUDE