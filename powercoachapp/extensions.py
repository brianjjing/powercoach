from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

socketio = SocketIO()
login_manager = LoginManager()
db = SQLAlchemy()