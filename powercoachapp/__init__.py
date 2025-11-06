from flask import Flask
from powercoachapp import auth, workout
from powercoachapp.extensions import socketio, db, logger
import os
from datetime import timedelta

#Factory function for creating remote app:
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    #For AWS Postgresql:
    DB_URI = f"postgresql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    
    # #Use this code for remote:
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = DB_URI,
        SECRET_KEY = os.environ.get("SECRET_KEY")
    )
    
    logger.debug("App database configured")
    
    # #Render:
    # app.config.from_mapping(
    #     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL"),
    #     SECRET_KEY = os.environ.get("SECRET_KEY") #Make this the actual secret key
    # )

    #logger.debug(os.environ.get("DATABASE_URL"))
    #logger.debug(app.config["SQLALCHEMY_DATABASE_URI"])
    
    #Local database:
    # db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    # db_url = f'sqlite:///{db_path}'
    # app.config.from_mapping(
    #     SQLALCHEMY_DATABASE_URI=db_url,
    #     SECRET_KEY=os.environ.get("SECRET_KEY", 'dev')
    # )

    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet', logger=logger, engineio_logger=logger, cors_allowed_origins='*')
    logger.debug("Database and SocketIO initialized")

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
    
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=48)

    # --- THIS IS THE CORRECT LOCATION FOR THE HEALTH CHECK ENDPOINT ---
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Returns a simple success message for health checks.
        """
        # You can add more logic here, e.g., check database connection
        logger.info("Health check response sent: OK, 200")
        return "OK", 200

    app.register_blueprint(auth.authbp)
    app.register_blueprint(workout.workoutbp)

    #Creating the models from sqlmodels.py in database.db:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

    return app