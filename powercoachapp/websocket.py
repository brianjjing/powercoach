import sys
from powercoachapp import powercoach
sys.path.append("/Users/brian/Documents/Python/PowerCoach")
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
def handle_test_message(data):
    sid = request.sid
    print(f"Received debug message: {data}")
    emit('debug_message', {'status': 'received'})

#MAKING A SLIGHT CHANGE TO SEE WHAT BRANCH ON GITHUB THIS IS ON

powercoach_live = False
@socketio.on('start_powercoach_stream')
def handle_start_stream():
    sid = request.sid
    powercoach_messages = powercoachalg(sid)
    global powercoach_live
    powercoach_live = True
    for json_data in powercoach_messages:
        if sid not in active_clients:
            print(f"Client {sid} not an active client anymore. Stopping stream.")
            break
        if powercoach_live == False:
            print(f"Powercoach stream ended.")
            break
        emit('powercoach_message', json_data, to = sid)
        print(json_data)
        socketio.sleep(0.1)
        
@socketio.on('stop_powercoach_stream')
def handle_stop_stream():
    global powercoach_live
    powercoach_live = False
    print("powercoach_live set to False")