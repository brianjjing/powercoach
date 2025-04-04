#FIXING THE NO MODULE NAMED POWERCOACHAPP ERROR:
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'powercoachapp'))

from flask import Flask, render_template
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from powercoachapp.extensions import socketio

#Factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    #__name__ is a built in ATTRIBUTE. That's why it can't be simplified past the built-in '__[]__' form. This creates a Flask instance (or an app) named powercoach.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config["DEBUG"] = True
    
    #Defining the websocket object and initializing it:
    socketio.init_app(app, async_mode='eventlet', logger = True, engineio_logger=True, cors_allowed_origins='*')
    #
    
    from powercoachapp import websocket

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

    #@app.route('/')
    #def homepage():
    #    return render_template('home/homepage.html')
        
    #Registering the blueprints:
    from powercoachapp import homepage
    app.register_blueprint(homepage.homepagebp)
    from powercoachapp import auth
    from powercoachapp import powercoach
    app.register_blueprint(auth.authbp)
    app.register_blueprint(powercoach.powercoachbp)
    
    #Initializing database:
    from powercoachapp import database
    database.init_app(app)
    
    return app