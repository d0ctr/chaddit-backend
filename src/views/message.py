from flask import request, Blueprint, g
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
@Auth.auth_required
def get_messages_for_chat(chat_id):
  chat = ChatModel.get_by_id(chat_id)
  if not chat:
    return custom_response({'error': 'Chat no found.'}, 404)
  if g.user.get('user_id') not in [participant.user_id for participant in chat.participants]:
    return custom_response({'error': 'You are not a member of this chat.'}, 403)
  ser_messages = message_schema.dump(MessageModel.get_by_chat(chat_id), many = True)
  return custom_response(ser_messages, 200)

@message_api.route('/message', methods = ['POST'])
@CurrentWorkspace.chat_required
@Auth.auth_required
def create_message():
  req_data = request.get_json()
  try:
    ser_message = message_schema.load(req_data)
  except ValidationError as err:
    return custom_response({'error': 'Invalid message scheme was provided.'}, 400)
    
  if not ser_message.get('body'):
    return custom_response({'error': 'Message must have a body.'}, 400)
  ser_message['chat_id'] = g.chat.get('chat_id')
  ser_message['author_id'] = g.user.get('user_id')
  message = MessageModel(ser_message)
  message.save()
  ser_message = message_schema.dump(message)
  socketio.emit('new message', ser_message)
  return custom_response(ser_message, 201)

  