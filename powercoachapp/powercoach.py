from zoneinfo import ZoneInfo
from datetime import datetime
from flask import Blueprint, g, request, jsonify
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import Workout

powercoachsessionbp = Blueprint('powercoachsession', __name__, url_prefix='/powercoachsession')

# THIS WILL BE USED FOR THE STARTPOWERCOACH INSTEAD OF THE WEBSOCKET EMMITTING:
#(since it's a one-time event. but for handling the frames after that, use handle_frame())

#Workout Creation Route:
@powercoachsessionbp.route('/startpowercoach', methods=['POST'])
@login_required
def start_powercoach():
    powercoach_session_data = request.get_json()
    #Get start time and exercise, then store it (dont do start time every time)
    
    if not powercoach_session_data:
        return jsonify({"start_powercoach_message": "Unexpected error occurred - please try again."}), 400
    
    logger.info(powercoach_session_data)
    
    #All lists:
    start_time = powercoach_session_data['start_time']
    exercise = powercoach_session_data['exercise']
    
    if not start_time:
        return jsonify({
            "start_powercoach_message": f"Unexpected error occurred - please try again."
        }), 400
    if not exercise:
        return jsonify({
            "start_powercoach_message": "Select an exercise!"
        }), 400
      
    try:
        ...
    except Exception as e:
        logger.debug(f"Error starting powercoach: {e}")
        #RESET THE R_CONN FOR THIS SID.
        return jsonify({
            "start_powercoach_message": "Sorry, an error occurred. Please try again."
        }), 500

#Do it for start_powercoach