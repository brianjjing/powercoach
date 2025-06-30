import sys
import os
import logging
from flask_socketio import emit
from flask import request
from powercoachapp.extensions import socketio, logger
from powercoachapp.OLDpowercoachalgs import powercoachalg, active_clients

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
    
@socketio.on('test')
def bruh():
    print("TEST RESPONSE PRINT")
    logger.info(f"TEST RESPONSE LOGGER OBJECT")
    logging.info("TEST RESPONSE LOGGING")
    emit('test_response', {'status': 'received'})


@socketio.on('test_message')
def handle_test_message(message):
    sid = request.sid
    logger.info(f"RECEIVED TEST MESSAGE FRM USER {sid}: {message}")
    logging.info("RECEIVED DA TEST MESSAGE, LOGGING")
    emit('test_response', {'status': 'received'})

#PRINT AS LOGS (IMPORT LOGGING --> LOGGING.INFO("MESSAGE"))
@socketio.on('handle_powercoach_frame') #will become handle_deadlift_frame
def handle_powercoach_frame(base64_string):
    logger.info("POWERCOACH FRAME RECEIVED")
    logger.info(f"Length of base64_string[0]: {len(base64_string)}")
    logger.info(f"Byte size: {sys.getsizeof(base64_string)}")
    powercoach_message = powercoachalg(base64_string)
    logger.info("Powercoach alg done on the frame")
    emit('powercoach_message', [powercoach_message])
    logger.info("Powercoach message emitted")