from flask_socketio import emit, SocketIOTestClient
import requests
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp import create_app
from powercoachapp.OLDpowercoachalgs import powercoachalg, active_clients

app = create_app()

client = SocketIOTestClient(app, socketio)
client.connect()

# Now when you call emit, it will log the message
client.emit('test_message')
#client.emit('start_powercoach_stream')
#Problem: stuck on one emit line with no way to stop powercoach stream
print("Other events are being listened to")

client.emit('stop_powercoach_stream')