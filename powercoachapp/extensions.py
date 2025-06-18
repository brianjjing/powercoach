from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging

socketio = SocketIO()
login_manager = LoginManager()
db = SQLAlchemy()
logger = logging.getLogger(__name__)