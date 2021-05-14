from flask_socketio import SocketIO

socketio = SocketIO(logger=True, engineio_logger=True, async_mode='eventlet')

__all__ = []