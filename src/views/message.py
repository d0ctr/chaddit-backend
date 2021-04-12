from flask import request, json, Blueprint, g
from marshmallow import ValidationError
from ..socketio import socketio
from ..models import MessageModel, ChatModel, UserModel
from ..schemas import MessageSchema
from ..shared.authetification import Auth
from ..shared.responses import custom_response
from ..shared.utils import CurrentWorkspace

message_api = Blueprint('messages', __name__)
message_schema = MessageSchema()

@message_api.route('/messages/<int:chat_id>', methods = ['GET'])
def get_messages_for_chat(chat_id):
  ser_messages = message_schema.dump(MessageModel.get_by_chat(chat_id), many = True)
  return custom_response(ser_messages, 200)

@message_api.route('/message', methods = ['POST'])
@CurrentWorkspace.chat_required
@Auth.auth_required
def create_message():
  req_data = request.get_json()
  ser_message = message_schema.load(req_data)
  if not ser_message.get('body'):
    return custom_response({'error': 'Message must have a body.'}, 400)
  ser_message['chat_id'] = g.chat.get('chat_id')
  ser_message['author_id'] = g.user.get('user_id')
  message = MessageModel(ser_message)
  message.save()
  ser_message = message_schema.dump(message)
  socketio.emit('new message', ser_message)
  return custom_response(ser_message, 201)

  