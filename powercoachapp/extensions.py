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

#EXTENSION:
shared_data = {
    'start_time': 0,
    'frame_height': None,
    'frame_width': None,
    'message': 'BARBELL NOT IN FRAME',
    'bar_bbox': None,
    'confidence': 0,
    'lift_stage': 'concentric',
    'equipment_type': 'barbell', #Use this later once you have the dumbbell and bodyweight and machine stuff set up
    'exercise': 'Conventional Deadlift'
}