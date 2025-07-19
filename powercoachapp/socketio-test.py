from flask_socketio import SocketIOTestClient
from powercoachapp.extensions import socketio
from powercoachapp import create_app

app = create_app()

client = SocketIOTestClient(app, socketio)

#client.connect()

client.emit('test')
client.emit('test_message', 'bruh')