import sys
from urllib import response
sys.path.append("/Users/brian/Documents/Python/PowerCoach")
from flask_socketio import emit, SocketIOTestClient
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp import create_app
from powercoachapp.powercoachalgs import powercoachalg, active_clients
import time

app = create_app()

client = SocketIOTestClient(app, socketio)

client.connect()

client.emit('test_message', 'TEST DATA')

client.emit('start_powercoach_stream')
#Problem: stuck on one emit line with no way to stop powercoach stream
print("Other events are being listened to")

client.emit('stop_powercoach_stream')