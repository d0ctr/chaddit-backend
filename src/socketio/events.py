from flask import json, Blueprint, g
from .socketio import socketio
from ..models import MessageModel, ChatModel, UserModel
from ..schemas import MessageSchema

message_schema = MessageSchema()

@socketio.route('/messages/<int:chat_id>', methods = ['GET'])
def get_messages_for_chat(chat_id):
  ser_messages = message_schema.dump(MessageModel.get_by_chat(chat_id), many = True)
  return custom_response(ser_messages, 200)

@socketio.on('new message')
def new_message(json):
  ser_message = message_schema.load(json)
  if not ser_message.get('body'):
    emit('error', {'error': 'Message must have a body.'})
    return
  if not ser_message.get('chat_id'):
    emit('error', {'error': 'Message must be in chat.'})
  if not ser_message.get('author_id'):
    emit('error', {'error': 'Message must have an author.'})
  message = MessageModel(ser_message)
  message.save()
  ser_message = message_schema.dump(message)
  emit('new message', ser_message)


@socketio.on('connect')
def connect(json)
  print('user connected')

