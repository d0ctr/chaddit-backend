from . import fields, Schema

class TopicTagSchema(Schema):
  tag_id = fields.Int()
  topic_id = fields.Int()
  tag = fields.Str()