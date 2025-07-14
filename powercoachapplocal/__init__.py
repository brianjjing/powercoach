from flask import Flask
from powercoachapplocal import powercoach
from powercoachapplocal.extensions import socketio, db
import os

#Factory function FOR LOCAL TESTING:
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    db_url = f'sqlite:///{db_path}'
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=db_url,
        SECRET_KEY=os.environ.get("SECRET_KEY", 'dev')
    )
    
    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet', logger = True, engineio_logger=True, cors_allowed_origins='*')
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.register_blueprint(powercoach.powercoachbp)
    
    return app