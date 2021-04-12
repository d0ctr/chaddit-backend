from . import fields, Schema, EXCLUDE

class TopicSchema(Schema):
  topic_id = fields.Int(dump_only = True)
  topic_title = fields.Str()
  created_at = fields.DateTime(dump_only = True)
  updated_at = fields.DateTime(dump_only = True)
  author_id = fields.Int()
  tags = fields.Nested('TopicTagSchema', many = True, allow_none = False)
  image = fields.Raw(allow_none = True)
  active = fields.Boolean()
  author = fields.Nested('UserSchema', dump_only = True)
  threads_count = fields.Int(dump_only = True)

  class Meta():
    unknown = EXCLUDE