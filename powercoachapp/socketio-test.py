import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'powercoachapp'))
from urllib import response
from flask_socketio import emit, SocketIOTestClient
import requests
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp import create_app
from powercoachapp.powercoachalgs import powercoachalg, active_clients
from socketio.packet import Packet

app = create_app()

client = SocketIOTestClient(app, socketio)

engine_url = 'ws://127.0.0.1:5000/socket.io/?EIO=4&transport=websocket'

client.connect()

# Now when you call emit, it will log the message
client.emit('test_message')
#client.emit('start_powercoach_stream')
#Problem: stuck on one emit line with no way to stop powercoach stream
print("Other events are being listened to")

client.emit('stop_powercoach_stream')