import sys
import os
from flask_socketio import emit
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp.powercoachalgs import powercoachalg, active_clients

@socketio.on('connect')
def handle_connect():
    print("Client connecting.")
    active_clients.add(request.sid)
    print("Client added to active clients.")
    print("Server is emitting connection event to client:")
    emit('connect_message', {'json_data': f'Client {request.sid} connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnecting.")
    if request.sid in active_clients:
        active_clients.remove(request.sid)
    print("Client removed from active clients.")
    emit('disconnect_message', {'json_data': f'Client {request.sid} disconnected'})
    
@socketio.on('test_message')
def handle_test_message(message):
    sid = request.sid
    print(f"Received test message from user {sid}: {message}")
    emit('test_response', {'status': 'received'})

@socketio.on('start_powercoach_stream')
def handle_start_stream():
    emit('powercoach_connection', ['PowerCoach connected'])
    print("PowerCoach connected")
    
#PRINT AS LOGS (IMPORT LOGGING --> LOGGING.INFO("MESSAGE"))
@socketio.on('handle_powercoach_frame')
def handle_powercoach_frame(base64_string):
    print("POWERCOACH FRAME RECEIVED", flush=True)
    powercoach_message = powercoachalg(base64_string[0])
    print("Powercoach alg done on the frame", flush=True)
    emit('powercoach_message', [powercoach_message])
    print("Powercoach message emitted", flush=True)

@socketio.on('stop_powercoach_stream')
def handle_stop_stream():
    emit('powercoach_disconnection', ['PowerCoach disconnected. Connecting...'])
    print("PowerCoach disconnected")