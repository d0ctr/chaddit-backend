from flask import request, Blueprint, g
from marshmallow import ValidationError
from ..models import PostModel
from ..schemas import PostSchema
from ..shared.authetification import Auth
from ..shared.responses import custom_response
from ..shared.utils import CurrentWorkspace

post_api = Blueprint('posts', __name__)
post_schema = PostSchema()

@post_api.route('/posts', methods = ['GET'])
@CurrentWorkspace.thread_required
def get_posts_from_thread():
  offset = request.args.get('offset', default = 0, type = int)
  limit = request.args.get('limit', default = 20, type = int)
  post = PostModel.get_by_thread_id(g.thread.get('thread_id'))[0]
  ser_post = post_schema.dump(post)
  if limit == 0:
    ser_post['responses'] = ser_post.get('responses')[offset:]
  else:
    ser_post['responses'] = ser_post.get('responses')[offset:limit + offset]
  return custom_response(ser_post, 200)

@post_api.route('/post/<int:post_id>', methods = ['GET'])
def get_post(post_id):
  post =  PostModel.get_by_id(post_id)
  if not post:
    return custom_response({'error': 'Post not found.'}, 404)
  ser_post = post_schema.dump(post)
  return custom_response(ser_post, 200)

@post_api.route('/posts/<int:root_post_id>', methods = ['GET'])
def get_posts_from_root(root_post_id):
  offset = request.args.get('offset', default = 0, type = int)
  limit = request.args.get('limit', default = 20, type = int)
  posts = PostModel.get_by_root_post_id(root_post_id)
  if not posts:
    return custom_response({'error': 'Posts not found.'}, 400)
  if limit == 0:
    ser_posts = post_schema.dump(posts[offset:], many = True)
  else:
    ser_posts = post_schema.dump(posts[offset:offset + limit], many = True)
  return custom_response(ser_posts, 200)

@post_api.route('/post', methods = ['POST'])
@Auth.auth_required
@CurrentWorkspace.thread_required
@CurrentWorkspace.post_required
def create_post():
  req_data = request.get_json()
  try:
    ser_post = post_schema.load(req_data)
  except ValidationError as err:
    return custom_response({'error': 'Invalid post scheme was provided.'}, 400)
  
  ser_post['author_id'] = g.user.get('user_id')
  ser_post['thread_id'] = g.thread.get('thread_id')
  ser_post['root_post_id'] = g.post.get('post_id')

  if not ser_post.get('body'):
    return custom_response({'error': 'Post must have a body.'}, 400)
  post = PostModel(ser_post)
  post.save()
  ser_post = post_schema.dump(post)
  return custom_response(ser_post, 201)
