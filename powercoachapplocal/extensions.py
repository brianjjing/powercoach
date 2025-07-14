from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging, sys

socketio = SocketIO()

clients = set()
login_manager = LoginManager()
db = SQLAlchemy()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)

#TEST EXTENSION:
shared_data = {
    'start_time': 0,
    'original_frame': None,
    'frame_height': None,
    'frame_width': None,
    'message': 'BARBELL NOT IN FRAME',
    'bar_bbox': None,
    'deadlift_stage': 1
}