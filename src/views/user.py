from flask import request, json, Response, Blueprint, g, redirect, url_for
from marshmallow import ValidationError
from ..models.user import UserModel
from ..schemas.user import UserSchema
from ..shared.authetification import Auth
from ..shared.constants import RoleId
from ..shared.responses import custom_response

user_api = Blueprint('users', __name__)
user_schema = UserSchema()

def email_exists(email):
  if UserModel.get_by_email(email):
    return True
  return False

@user_api.route('/user', methods = ['GET', 'PATCH'])
@Auth.auth_required
def user():
  return redirect(url_for('users.get_user', user_id = g.user.get('user_id')), code = 307)


@user_api.route('/register', methods = ['POST'])
def register():
  req_data = request.get_json()
  ser_user = user_schema.load(req_data)
  if email_exists(ser_user.get('user_email')):
    message = {'error' : 'User with this email already exists.'}
    return custom_response(message, 400)

  user = UserModel(ser_user)
  user.save()

  token, error = Auth.generate_token(user_schema.dump(user).get('user_id'))
  if error:
    return custom_response(error, 500)
  return custom_response({'api_token' : token}, 201)

@user_api.route('/login', methods = ['POST'])
def login():
  req_data = request.get_json()
  ser_user = user_schema.load(req_data, partial=True)

  if not ser_user.get('user_email') or not ser_user.get('user_pass'):
    return custom_response({'error': 'Email and password are required to login.'}, 400)

  user = UserModel.get_by_email(ser_user.get('user_email'))
  if not user:
    return custom_response({'error': 'Invalid email.'}, 400)
  if not user.check_hash(ser_user.get('user_pass')):
    return custom_response({'error': 'Invalid password.'}, 400)
    
  ser_user = user_schema.dump(user)
  if ser_user.get('active') == False:
    return custom_response({'error': 'This user is not active.'}, 400)
  token, error = Auth.generate_token(ser_user.get('user_id'))
  if error:
    return custom_response(error, 500)
  return custom_response({'api_token': token}, 200)

@user_api.route('/user/<int:user_id>', methods = ['GET'])
@Auth.auth_required
def get_user(user_id):
  user = UserModel.get_by_id(user_id)
  if not user:
    return custom_response({'error' : 'User not found.'}, 404)
  
  ser_user = user_schema.dump(user)
  if (g.user.get('user_id') != ser_user.get('user_id')) and (g.user.get('role_id') != RoleId.ADMINISTRATOR):
    del ser_user['user_email']
  return custom_response(ser_user, 200)

@user_api.route('/user/<int:user_id>', methods = ['PATCH'])
@Auth.auth_required
def update_user(user_id):
  req_data = request.get_json()
  ser_user = user_schema.load(req_data, partial = True)

  updating_user = UserModel.get_by_id(user_id)
  if not updating_user:
    return custom_response({'error': 'User not found'}, 404)
  if (user_id == g.user.get('user_id')) or (g.user.get('role_id') == RoleId.ADMINISTRATOR):
    user_pass = ser_user.get('user_pass')
    
    if user_pass:
      if g.user.get('role_id') == RoleId.USER:
        if not updating_user.check_hash(user_pass):
          old_pass = req_data.get('old_user_pass')
          if old_pass and (not updating_user.check_hash(old_pass)):
            return custom_response({'error' : 'Old password does not fit.'}, 400)

    updating_user.update(ser_user)
    ser_user = user_schema.dump(updating_user)
    return custom_response(ser_user, 200)
  else:
    return custom_response({'error' : 'You do not have permission to edit this user.'}, 403)

@user_api.route('/users', methods = ['GET'])
@Auth.auth_required
def get_all():
  if g.user.get('role_id') == RoleId.ADMINISTRATOR:
    users = UserModel.get_all()
    ser_users = user_schema.dump(users, many = True)
    return custom_response(ser_users, 200)
  else:
    return custom_response({'error' : 'You do not have permission to access this data.'}, 403)
