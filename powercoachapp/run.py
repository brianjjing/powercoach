import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'powercoachapp'))
from powercoachapp import create_app, socketio
from flask import request

#import logging
#logging.basicConfig(level=logging.DEBUG)

app = create_app()

@app.before_request
def log_request():
    # Log the full request headers
    print(f"Incoming request method: {request.method}")
    print(f"Request URL: {request.url}")
    print("Request Headers:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=13030, debug=True)