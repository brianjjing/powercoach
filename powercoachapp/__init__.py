from flask import Flask
from powercoachapp import auth
from powercoachapp.extensions import socketio, db, logger
from powercoachapp.sqlmodels import User
import os

#Factory function for creating remote app:
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    #Use this code for render:
    # app.config.from_mapping(
    #     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL"),
    #     SECRET_KEY = os.environ.get("SECRET_KEY", 'dev')
    # )

    # logger.debug(os.environ.get("DATABASE_URL"))
    # logger.debug(app.config["SQLALCHEMY_DATABASE_URI"])
    
    
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    db_url = f'sqlite:///{db_path}'
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=db_url,
        SECRET_KEY=os.environ.get("SECRET_KEY", 'dev')
    )

    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet', logger=logger, engineio_logger=logger, cors_allowed_origins='*')

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

    #Creating the models from sqlmodels.py in database.db:
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="brian").first():
            base_user = User(
                username="brian",
                password="test123"  # or whatever password you want
            )
            db.session.add(base_user)
            db.session.commit()

    return app