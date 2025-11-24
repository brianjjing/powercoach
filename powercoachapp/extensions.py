from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging, sys

socketio = SocketIO()

clients = set()
redis_clients = {}
login_manager = LoginManager()
db = SQLAlchemy()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)

#Sliding window data:
sliding_window_framework_metadata = {
    'WINDOW_LEN': 4,          # SEQUENCE LENGTH: Set to 4 frames for low latency testing
    'N_MOTION_CLASSES': 2,
    'N_FEATURES': 10,         # Total number of kinematic features (Input size for both models)
    'N_HMM_STATES': 5,        # 0: Setup, 1: Eccentric, 2: Concentric, 3: Lockout, 4: Stretch
    'N_FAULT_CLASSES': 2,     # 0: No Clapping, 1: Clapping Motion
    'MODEL_WEICHTS_PATH': 'clapping_cnn_weights.h5',
    'HOP_SIZE': 2,
    'DEVICE': 'CPU',          
    'CONFIDENCE_THRESHOLD': 0.8
}