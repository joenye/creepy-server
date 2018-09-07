"""Configures websocket event handlers"""
from flask_socketio import SocketIO


def configure_handlers(socketio: SocketIO):
    @socketio.on('message')
    def handle_message(message):
        print('received message: ' + message)

    @socketio.on('json')
    def handle_json(json):
        print('received json: ' + str(json))
