import os
from flask import Flask
from powercoachapp import auth, powercoach
from powercoachapp.extensions import socketio, db
from powercoachapp.sqlmodels import User

#Factory function
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'databases/logins.db'),
        SECRET_KEY='dev'
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

    app.register_blueprint(auth.authbp)
    app.register_blueprint(powercoach.powercoachbp)
    
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