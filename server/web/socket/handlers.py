"""Configures websocket event handlers"""
import logging

from flask_socketio import SocketIO, emit


logger = logging.getLogger(__name__)


def configure_handlers(socketio: SocketIO):
    ##############
    #  Standard  #
    ##############

    @socketio.on('connect')
    def handle_connect():
        logger.warn('received new connection')

    @socketio.on('message')
    def handle_message(message):
        logger.warn('received message: ' + str(message))

    @socketio.on('json')
    def handle_json(message):
        logger.warn('received json: ' + str(message))

    ############
    #  Custom  #
    ############
