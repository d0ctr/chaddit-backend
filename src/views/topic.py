from flask import request, json, Response, Blueprint, g, redirect, url_for
from marshmallow import ValidationError
from ..models.topic import TopicModel
from ..schemas.topic import TopicSchema
from ..shared.authetification import Auth
from ..shared.utils import CurrentWorkspace
from ..shared.responses import custom_response
from ..shared.constants import RoleId

topic_api = Blueprint('topics', __name__)
topic_schema = TopicSchema()

@topic_api.route('/topic', methods = ['GET', 'PATCH', 'DELETE'])
@CurrentWorkspace.topic_required
def topic():
  return redirect(url_for('topics.get_topic', topic_id = g.topic.get('topic_id')), 307)

@topic_api.route('/topic/<int:topic_id>', methods = ['GET'])
def get_topic(topic_id):
  topic = TopicModel.get_by_id(topic_id)
  if not topic:
    return custom_response({'error': 'Topic not found.'}, 404)
  ser_topic = topic_schema.dump(topic)
  return custom_response(ser_topic, 200)

@topic_api.route('/topics', methods = ['GET'])
def get_all():
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    topics = TopicModel.get_all(orderby=orderbyasc, order='asc').all()
    ser_topics = topic_schema.dump(topics, many = True)
  elif orderbydesc:
    topics = TopicModel.get_all(orderby=orderbydesc, order='desc').all()
    ser_topics = topic_schema.dump(topics, many = True)
  else:
    topics = TopicModel.get_all().all()
    ser_topics = topic_schema.dump(topics, many = True)
    
  return custom_response(ser_topics, 200)

@topic_api.route('/topic', methods = ['POST'])
@Auth.auth_required
def create_topic():
  try:
    req_data = request.get_json()
    ser_topic = topic_schema.load(req_data)
  except:
    print('\nError while loading req_data:\n', req_data)
  
  ser_topic['author_id'] = g.user.get('user_id')

  if ser_topic.get('topic_title'):
    if not isinstance(ser_topic.get('tags'), list):
      return custom_response({'error': 'Topic must contain at least one tag.'}, 400)
    topic = TopicModel(ser_topic)
    topic.save()
    ser_topic = topic_schema.dump(topic)
    return custom_response(ser_topic, 201)
  else:
    return custom_response({'error': 'Topic must have a title.'}, 400)

@topic_api.route('/topic/<int:topic_id>', methods = ['PATCH'])
@Auth.auth_required
def update_topic(topic_id):
  if not ((g.user.get('role_id') == RoleId.ADMINISTRATOR) or (g.user.get('role_id') == RoleId.MODERATOR)):
    return custom_response({'error' : 'You do not have permission to edit this content.'}, 403)
  
  req_data = request.get_json()
  ser_topic = topic_schema.load(req_data, partial = True)

  updating_topic = TopicModel.get_by_id(topic_id)
  if not updating_topic:
    return custom_response({'error': 'Topic not found.'}, 404)

  updating_topic.update(ser_topic)
  ser_topic = topic_schema.dump(updating_topic)
  return custom_response(ser_topic, 200)

@topic_api.route('/topic/<int:topic_id>', methods = ['DELETE'])
@Auth.auth_required
def delete_topic(topic_id):
  if not ((g.user.get('role_id') == RoleId.ADMINISTRATOR) or (g.user.get('role_id') == RoleId.MODERATOR)):
    return custom_response({'error' : 'You do not have permission to edit this content.'}, 403)
  
  deleting_topic = TopicModel.get_by_id(topic_id)
  if not deleting_topic:
    return custom_response({'error' : 'Topic not found.'}, 404)

  deleting_topic.delete()
  return custom_response({}, 204)