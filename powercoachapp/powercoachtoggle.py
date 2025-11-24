from flask import Blueprint, g, request, jsonify, session
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger, sliding_window_framework_metadata, active_form_correctors
from powercoachapp.powercoachalg import SlidingWindowFormCorrector

powercoachsessionbp = Blueprint('powercoachsession', __name__, url_prefix='/powercoachsession')

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
        user_id = g.user.id
        corrector = SlidingWindowFormCorrector(window_size=sliding_window_framework_metadata['WINDOW_LEN'], n_features=sliding_window_framework_metadata['N_FEATURES'], n_hmm_states=sliding_window_framework_metadata['N_HMM_STATES'], n_fault_classes=sliding_window_framework_metadata['N_FAULT_CLASSES'])
        active_form_correctors[user_id] = corrector
        return jsonify({
            "start_powercoach_message": "Powercoach successfully started!"
        }), 200
    except Exception as e:
        logger.debug(f"Error starting powercoach: {e}")
        return jsonify({
            "start_powercoach_message": "Sorry, an error occurred. Please try again."
        }), 500

@powercoachsessionbp.route('/stoppowercoach', methods=['POST'])
@login_required
def stop_powercoach():
    try:
        user_id = g.user.id
        if user_id in active_form_correctors:
            del active_form_correctors[user_id]
            
            logger.info(f"PowerCoach session stopped and cleaned up for user {user_id}")

            return jsonify({
                "stop_powercoach_message": "PowerCoach session stopped successfully."
            }), 200
    except Exception as e:
        logger.debug(f"Error stopping powercoach: {e}")
        return jsonify({
            "stop_powercoach_message": "Sorry, an error occurred. Please try again."
        }), 500