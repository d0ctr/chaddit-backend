from flask import request, json, Response, Blueprint, g, redirect, url_for
from marshmallow import ValidationError
from ..socketio import socketio
from ..models import ChatModel, UserModel
from ..schemas import ChatSchema
from ..shared.authetification import Auth
from ..shared.responses import custom_response
from ..shared.utils import CurrentWorkspace

chat_api = Blueprint('chats', __name__)
chat_schema = ChatSchema()

@chat_api.route('/chat/<int:chat_id>', methods = ['GET'])
@Auth.auth_required
def get_chat(chat_id):
  chat = ChatModel.get_by_id(chat_id)
  if not chat:
    return custom_response({'error' : 'Chat not found.'}, 404)
  ser_chat = chat_schema.dump(chat)
  return custom_response(ser_chat, 200)

@chat_api.route('/chat', methods = ['POST'])
@Auth.auth_required
def create_chat():
  req_data = request.get_json()
  ser_chat = chat_schema.load(req_data)
  topic_id = req_data.get('topic_id')
  vacant_chat = ChatModel.get_vacant_chat(user_id = g.user.get('user_id'), topic_id = topic_id)
  if not vacant_chat:
    chat = ChatModel(ser_chat)
    user = UserModel.get_by_id(g.user.get('user_id'))
    user.chats.append(chat)
    chat.save()
    ser_chat = chat_schema.dump(chat) 
  else:
    another_user = vacant_chat.participants[0]
    user = UserModel.get_by_id(g.user.get('user_id'))
    user.chats.append(vacant_chat)
    vacant_chat.full = True
    ser_vacant_chat = chat_schema.dump(vacant_chat)
    vacant_chat.update(ser_vacant_chat)
    ser_chat = chat_schema.dump(vacant_chat)
    socketio.emit('new join', ser_chat)
  return custom_response(ser_chat, 201)

@chat_api.route('/chats', methods = ['GET'])
@Auth.auth_required
def get_chats():
  chats = ChatModel.get_by_user(g.user.get('user_id'))
  ser_chats = chat_schema.dump(chats, many = True)
  return custom_response(ser_chats, 200)