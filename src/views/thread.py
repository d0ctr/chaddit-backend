from flask import request, json, Response, Blueprint, g, redirect, url_for
from marshmallow import ValidationError
from ..models import ThreadModel, PostModel
from ..schemas import ThreadSchema, PostSchema
from ..shared.authetification import Auth
from ..shared.responses import custom_response
from ..shared.utils import CurrentWorkspace
from ..shared.constants import RoleId

thread_api = Blueprint('threads', __name__)
thread_schema = ThreadSchema()
post_schema = PostSchema()

@thread_api.route('/thread', methods = ['GET', 'PATCH', 'DELETE'])
@CurrentWorkspace.thread_required
def thread():
  if request.method == 'GET':
    return redirect(url_for('threads.get_thread', thread_id = g.thread.get('thread_id')), 307)
  elif request.method == 'PATCH':
    return redirect(url_for('threads.update_thread', thread_id = g.thread.get('thread_id')), 307)
  elif request.method == 'DELETE':
    return redirect(url_for('threads.delete_thread', thread_id = g.thread.get('thread_id')), 307)

@thread_api.route('/threads', methods = ['GET'])
@CurrentWorkspace.topic_required
def get_from_topic():
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    threads = ThreadModel.get_by_topic_id(g.topic.get('topic_id'), orderby = orderbyasc, order = 'asc').all()
    ser_threads = thread_schema.dump(threads, many = True)
  elif orderbydesc:
    threads = ThreadModel.get_by_topic_id(g.topic.get('topic_id'), orderby = orderbydesc, order = 'desc').all()
    ser_threads = thread_schema.dump(threads, many = True)
  else:
    threads = ThreadModel.get_by_topic_id(g.topic.get('topic_id')).all()
    ser_threads = thread_schema.dump(threads, many = True)
  
  return custom_response(ser_threads, 200)

@thread_api.route('/thread/<int:thread_id>', methods = ['GET'])
def get_thread(thread_id):
  thread = ThreadModel.get_by_id(thread_id)
  if not thread:
    return custom_response({'error': 'Thread not found.'}, 404)
  thread.views = ThreadModel.views + 1
  thread.update({})
  ser_thread = thread_schema.dump(thread)
  return custom_response(ser_thread, 200)

@thread_api.route('/thread', methods = ['POST'])
@Auth.auth_required
@CurrentWorkspace.topic_required
def create_thread():
  req_data = request.get_json()
  try:
    ser_thread = thread_schema.load(req_data)
  except ValidationError as err:
    return custom_response({'error': 'Invalid thread scheme was provided.'}, 400)
  ser_thread['author_id'] = g.user.get('user_id')
  ser_thread['topic_id'] = g.topic.get('topic_id')

  if not ser_thread.get('thread_title'):
    return custom_response({'error': 'Thread must have a title.'}, 400)
  elif not len(ser_thread.get('posts')):
    return custom_response({'error': 'Thread must contain root post.'}, 400)
  else:
    ser_root_post = post_schema.load(ser_thread.get('posts')[0])
    if not ser_root_post.get('body'):
      return custom_response({'error': 'Root post must have a body.'}, 400)

    thread = ThreadModel(ser_thread)
    thread.save()
    ser_thread = thread_schema.dump(thread)

    ser_root_post['thread_id'] = ser_thread.get('thread_id')
    ser_root_post['author_id'] = g.user.get('user_id')
    root_post = PostModel(ser_root_post)
    root_post.save()
    ser_thread = thread_schema.dump(thread)
    return custom_response(ser_thread, 201)

@thread_api.route('/thread/<int:thread_id>', methods = ['PATCH'])
@Auth.auth_required
def update_thread(thread_id):
  if not ((g.user.get('role_id') == RoleId.ADMINISTRATOR) or (g.user.get('role_id') == RoleId.MODERATOR)):
    return custom_response({'error' : 'You do not have permission to edit this content.'}, 403)

  req_data = request.get_json()
  try:
    ser_thread = thread_schema.load(req_data, partial = True)
  except ValidationError as err:
    return custom_response({'error': 'Invalid thread scheme was provided.'}, 400)

  updating_thread = ThreadModel.get_by_id(thread_id)
  if not updating_thread:
    return custom_response({'error': 'Thread not found.'}, 404)

  updating_thread.update(ser_thread)
  ser_thread = thread_schema.dump(updating_thread)
  return custom_response(ser_thread, 200)

@thread_api.route('/thread/<int:thread_id>', methods = ['DELETE'])
@Auth.auth_required
def delete_thread(thread_id):
  if not ((g.user.get('role_id') == RoleId.ADMINISTRATOR) or (g.user.get('role_id') == RoleId.MODERATOR)):
    return custom_response({'error' : 'You do not have permission to edit this content.'}, 403)
    
  deleting_thread = ThreadModel.get_by_id(thread_id)
  if not deleting_thread:
    return custom_response({'error': 'Thread not found.'}, 404)

  deleting_thread.delete()
  return custom_response({}, 204)