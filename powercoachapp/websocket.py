import datetime
import logging
from flask_socketio import emit
from flask import request, session
from powercoachapp.extensions import socketio, logger, clients
from powercoachapp.powercoachalg import powercoachalg

@socketio.on('connect')
def handle_connect():
    logger.info("Client connecting.")
    sid = request.sid
    logger.info(f"Client {sid} connecting.")
    clients.add(sid)
    logger.info("Client added to active clients.")

    emit('connect_message', {'json_data': f'Client {sid} connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnecting.")
    sid = request.sid
    
    if sid in clients:
        clients.remove(sid)
    logger.info(f"Client {sid} removed from active clients.")
    
    emit('disconnect_message', {'json_data': f'Client {sid} disconnected'})
    
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

# @socketio.on('start_powercoach')
# def start_powercoach(payload):
#     # Initialize a new dictionary in the session for the current workout
#     session['powercoach_data'] = {
#         'exercise': payload['exercise'],
#         'start_time': payload['start_time'],
#         'message': 'BARBELL NOT IN FRAME',
#         'bar_bbox': None,
#         'confidence': 0,
#         'lift_stage': 'concentric',
#     }
#     logger.info(f"Session data initialized for client {request.sid}: {session['powercoach_data']}")
    
#     emit('start_powercach_message', 'PowerCoach session initialized successfully.')

@socketio.on('handle_powercoach_frame')
def handle_powercoach_frame(jpeg_data):
    logger.info("POWERCOACH FRAME RECEIVED")
    logger.info(f"Jpeg data byte size: {len(jpeg_data)}")
    
    if 'powercoach_data' in session:
        logger.info(f"Processing frame for session: {session['powercoach_data']}")
        powercoachalg(jpeg_data)
        
        emit('powercoach_message', session['message'])
        logger.info("Powercoach message emitted")
    else:
        logger.warning(f"Received video frame from {request.sid}, but no active powercoach session found.")
        emit('powercoach_message', 'No active session to process video frames.')
        
@socketio.on('stop_powercoach')
def stop_powercoach():
    del session['powercoach_data']
    logger.info(f"Session data for client {request.sid} has been reset.")
    
    emit('stop_powercoach_message', 'PowerCoach session reset successfully.')