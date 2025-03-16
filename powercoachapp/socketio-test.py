import sys
sys.path.append("/Users/brian/Documents/Python/PowerCoach")
from flask_socketio import emit, SocketIOTestClient
from flask import request
from powercoachapp.extensions import socketio
from powercoachapp import create_app
from powercoachapp.powercoachalgs import powercoachalg, active_clients
import time

app = create_app()

client = SocketIOTestClient(app, socketio)

print("🔹 Sending 'start_powercoach_stream' event...")
client.emit('start_powercoach_stream')

# Step 3: Receive streamed responses (for a few frames)
for _ in range(10000):  # Receive 10 frames as a test
    response = client.get_received()
    if response:
        print(f"📡 Received stream update: {response}")
    else:
        print("No response")
    # Wait before receiving the next frame

# Step 4: Stop the PowerCoach stream
print("🔹 Sending 'stop_powercoach_stream' event...")
client.emit('stop_powercoach_stream')

# Close the test client
client.disconnect()