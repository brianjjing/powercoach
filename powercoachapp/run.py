import os
from powercoachapp import create_app, powercoachalg, bbelldetectioncreatemodel
from powercoachapp.auth import login_required
from powercoachapp.extensions import socketio, db, logger
from flask import request, session, g
from powercoachapp.sqlmodels import User, UserBackendData

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

@app.before_first_request
@login_required
def set_user_data():
    try:
        user_data_instance = UserBackendData.query.filter_by(
            user_id=g.user.id
        ).first()
        
        if user_data_instance:
            user_data_instance.start_time = 0
            user_data_instance.frame_height = 0
            user_data_instance.frame_width = 0
            user_data_instance.powercoach_message = "BARBELL NOT IN FRAME"
            user_data_instance.bar_bbox = None
            user_data_instance.confidence = 0.0
            user_data_instance.lift_stage = "concentric"
            user_data_instance.equipment_type = "barbell"
            user_data_instance.exercise = "conventional_deadlift"
            db.session.commit()
        else:
            new_user_data_instance = UserBackendData(
                start_time = 0,
                frame_height = 0,
                frame_width = 0,
                powercoach_message = "BARBELL NOT IN FRAME",
                bar_bbox = None,
                confidence = 0.0,
                lift_stage = "concentric",
                equipment_type = "barbell",
                exercise = "conventional_deadlift"
            )
            db.session.add(new_user_data_instance)
            db.session.commit()
        logger.info("User backend data set for the session.")
        
    except Exception as e:
        logger.error(f"Failed to set user data: {e}")
        #Handle more graciously next time

port = int(os.getenv("PORT", 10000))

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)