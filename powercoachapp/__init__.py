import os
from flask import Flask, render_template
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from powercoachapp.extensions import socketio, db

#Factory function
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'databases/logins.db'),
        SECRET_KEY='dev'
    )
    
    #Defining the websocket object and initializing it:
    socketio.init_app(app, async_mode='eventlet', logger = True, engineio_logger=True, ping_timeout=30, ping_interval=25, cors_allowed_origins='*')
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

    from powercoachapp.auth import authbp
    from powercoachapp.powercoach import powercoachbp
    app.register_blueprint(authbp)
    app.register_blueprint(powercoachbp)
    
    #Creating the models from sqlmodels.py in database.db:
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="brian").first():
            test_user = User(
                username="brian",
                password_hash="test123"  # or whatever password you want
            )
            db.session.add(test_user)
            db.session.commit()
    
    return app