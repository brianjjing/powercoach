import time
import logging
from flask_socketio import emit
from flask import request, g
from powercoachapp.extensions import socketio, logger, clients, shared_data, db
from powercoachapp.powercoachalg import powercoachalg
from powercoachapp.sqlmodels import UserBackendData

@socketio.on('connect')
def handle_connect():
    logger.info("Client connecting.")
    clients.add(request.sid)
    logger.info("Client added to active clients.")
    logger.info("Server is emitting connection event to client:")
    emit('connect_message', {'json_data': f'Client {request.sid} connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnecting.")
    if request.sid in clients:
        clients.remove(request.sid)
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

@socketio.on('start_powercoach')
def start_powercoach(performed_exercise):
    #Store the current exercise (performed_exercise) in the cache - USE THE DICTIONARY AT THE BOTTOM OF BARBELL.PY
    
    shared_data['message'] = 'BARBELL NOT IN FRAME'
    shared_data['bar_bbox'] = None
    shared_data['lift_stage'] = 'concentric'
    shared_data['start_time'] = time.time()
    logger.info("PowerCoach started")

#PRINT AS LOGS (IMPORT LOGGING --> LOGGING.INFO("MESSAGE"))
@socketio.on('handle_powercoach_frame')
def handle_powercoach_frame(jpegData):
    #from here, store selected_exercise in the cache.
    logger.info("POWERCOACH FRAME RECEIVED")
    logger.info(f"Jpeg data byte size: {len(jpegData)}")
    
    powercoachalg(jpegData)
    logger.info("Powercoach alg done on the frame")
    
    emit('powercoach_message', shared_data['message'])
    logger.info("Powercoach message emitted")
    
@socketio.on('stop_powercoach')
def stop_powercoach():
    shared_data['message'] = 'BARBELL NOT IN FRAME'
    shared_data['bar_bbox'] = None
    shared_data['lift_stage'] = 'concentric'
    shared_data['start_time'] = 0
    logger.debug("Powercoach stopped")
    
#WSGI server already handles the SIGTERM when shutting down the REMOTE server.
#Just need to manually kill connection when using the LOCAL server.