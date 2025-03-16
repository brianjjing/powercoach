import sys
sys.path.append("/Users/brian/Documents/Python/PowerCoach")
from flask_socketio import emit
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp.powercoachalgs import powercoachalg, active_clients

@socketio.on('connect')
def handle_connect():
    #active_clients.add(request.sid)
    print("Client connected.")
    #emit('connect_message', {'json_data': f'Client {request.sid} connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_clients:
        active_clients.remove(request.sid)
    print("Client disconnected.")
    emit('disconnect_message', {'json_data': f'Client {request.sid} disconnected'})
    
@socketio.on('test_message')
def handle_test_message(data):
    sid = request.sid
    print(f"Received debug message: {data}")
    emit('debug_message', {'status': 'received'})
    
@socketio.on('start_powercoach_stream')
def handle_start_stream():
    sid = request.sid
    for json_data in powercoachalg(sid):
        if sid not in active_clients:
            print(f"Client {sid} stopped PowerCoach stream. Stopping stream.")
            break
        emit('stream_update', json_data, to = sid)
        
@socketio.on('stop_powercoach_stream')
def handle_stop_stream():
    sid = request.sid
    if sid in active_clients:
        active_clients.remove(sid)
        print(f"Client {sid} stopped PowerCoach stream.")