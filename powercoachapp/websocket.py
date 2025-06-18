import sys
import os
import logging
from flask_socketio import emit
from flask import request
from powercoachapp.extensions import socketio, logger
from powercoachapp.powercoachalgs import powercoachalg, active_clients

@socketio.on('connect')
def handle_connect():
    logger.info("Client connecting.")
    active_clients.add(request.sid)
    logger.info("Client added to active clients.")
    logger.info("Server is emitting connection event to client:")
    emit('connect_message', {'json_data': f'Client {request.sid} connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnecting.")
    if request.sid in active_clients:
        active_clients.remove(request.sid)
    logger.info("Client removed from active clients.")
    emit('disconnect_message', {'json_data': f'Client {request.sid} disconnected'})
    
@socketio.on('test_message')
def handle_test_message(message):
    sid = request.sid
    logger.info(f"Received test message from user {sid}: {message}")
    emit('test_response', {'status': 'received'})

@socketio.on('start_powercoach_stream')
def handle_start_stream():
    logger.info("Powercoach stream started")
    emit('powercoach_connection', ['PowerCoach connected'])
    logger.info("PowerCoach connected")

#PRINT AS LOGS (IMPORT LOGGING --> LOGGING.INFO("MESSAGE"))
@socketio.on('handle_powercoach_frame')
def handle_powercoach_frame(base64_string):
    logger.info("POWERCOACH FRAME RECEIVED")
    logger.info(f"Length of base64_string[0]: {len(base64_string[0])}")
    logger.info(f"Byte size: {sys.getsizeof(base64_string[0])}")
    powercoach_message = powercoachalg(base64_string[0])
    logger.info("Powercoach alg done on the frame")
    emit('powercoach_message', [powercoach_message])
    logger.info("Powercoach message emitted")

@socketio.on('stop_powercoach_stream')
def handle_stop_stream():
    logger.info("Disconencting PowerCoach")
    emit('powercoach_disconnection', ['PowerCoach disconnected. Connecting...'])
    logger.info("PowerCoach disconnected")