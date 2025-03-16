import sys
sys.path.append("/Users/brian/Documents/Python/PowerCoach")
from powercoachapp import create_app, socketio

#import logging
#logging.basicConfig(level=logging.DEBUG)

app = create_app()

if __name__ == "__main__":
    socketio.run(app)