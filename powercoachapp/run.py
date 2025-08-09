import os
from powercoachapp import create_app, powercoachalg, extensions, auth, websocket, bbelldetectioncreatemodel
from powercoachapp.extensions import socketio, logger
from flask import request, session, g
from powercoachapp.sqlmodels import User


app = create_app()

@app.before_request
def log_request():
    # Log the full request headers
    print(f"Incoming request method: {request.method}")
    print(f"Request URL: {request.url}")
    print("Request Headers:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

#This ensures that before a request, your application checks the session,
#loads the user's data using Flask-SQLAlchemy, and makes it available via g.user. (current session user)
#(Knows it's the user doing it without having to requery the database every time.)
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    logger.info(f"Attempting to load user w/ user_id: {user_id}")

    #g is a global namespace for data for the app context at hand. Shares data across Flask app under the scope of a single request.
    #However, it only lasts for a request and does not persist. This sets g.user to the user id every request.
    if user_id is None:
        g.user = None
        logger.info(f"user_id not found. No session user.")
    else:
        g.user = User.query.get(user_id) #Works since id is the primary key integer. Searches the primary key col for user_id.
        logger.info(f"HTTP Request user: {g.user.username}")

port = int(os.getenv("PORT", 10000))

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)