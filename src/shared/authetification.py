import jwt, os, datetime
from flask import json, request, Response, g
from functools import wraps
from ..models.user import UserModel
from ..schemas.user import UserSchema
from .responses import custom_response

class Auth():
  @staticmethod
  def generate_token(user_id):
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
      }
      return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        'HS256'
      ).decode("utf-8"), None
    except Exception:
      return None, {'error': 'Error in generating user token.'}

  @staticmethod
  def decode_token(token):
    result = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
      result['data'] = {'user_id': payload['sub']}
      return result
    except jwt.ExpiredSignatureError:
      result['error'] = {'message': 'Token expired, please login again.'}
      return result
    except jwt.InvalidTokenError:
      result['error'] = {'message': 'Invalid token, please try again with a new token.'}
      return result

  @staticmethod
  def auth_required(func):
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        custom_response({'error' : 'Cannot access without token, login or sign up to get one.'}, 400)
        return custom_response({'error' : 'Cannot access without token, login or sign up to get one.'}, 400)
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return custom_response(data['error'], 400)
      
      user_id = data['data']['user_id']

      user = UserModel.get_by_id(user_id)

      if not user:
        return custom_response({'error' : 'User does not exist, invalid token.'}, 400)
        
      g.user = UserSchema().dump(user)
      if g.user.get('active') == False:
        return custom_response({'error' : 'This user is not active'}, 400)
      return func(*args, **kwargs)
    
    return decorated_auth