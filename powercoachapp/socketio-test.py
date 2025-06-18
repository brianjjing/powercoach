import sys
import os
from urllib import response
from flask_socketio import emit, SocketIOTestClient
import requests
from flask import request
from powercoachapp.extensions import socketio, logger
import logging
from powercoachapp import create_app, websocket, powercoachalgs

app = create_app()

client = SocketIOTestClient(app, socketio)

#client.connect()

client.emit('test')
client.emit('test_message', 'bruh')

received = client.get_received()
for i in received:
    print(i)

# client.emit('start_powercoach_stream')