from flask import Blueprint, g, request, jsonify
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import Workout

workoutbp = Blueprint('workout', __name__, url_prefix='/workout')

#Workout Creation Route:
@workoutbp.route('/createworkout', methods=['POST'])
@login_required
def create_workout():
    workout_data = request.get_json()
    
    if not workout_data:
        return jsonify({"workout_creation_message": "Please enter at least one exercise!"}), 400
    
    #All lists:
    name = workout_data['name']
    exercises = workout_data['exercises']
    sets = workout_data['sets']
    reps = workout_data['reps']
    weights = workout_data['weights']
    num_exercises = len(exercises)
    
    if Workout.query.filter_by(user_id=g.user.id, workout_name=name).first():
        return jsonify({
            "workout_creation_message": f"You already have a workout called {name}!"
        }), 409
    
    #RIGHT NOW IT'S A BAD LOOP: See what elements are missing.
    for exercise_index in num_exercises:
        if not exercises[exercise_index]:
            return jsonify({'workout_creation_message': 'Exercise name is required.', 'index': exercise_index}), 400
        elif not sets[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of sets is required.', 'index': exercise_index}), 400
        elif not reps[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of reps is required.', 'index': exercise_index}), 400
        elif not weights[exercise_index]:
            return jsonify({'workout_creation_message': 'Exercise weight is required.', 'index': exercise_index}), 400
    
    try:
        new_workout = Workout(
            workout_id = ..., #Get +1 of the current length of the table
            user_id = g.user.id,
            workout_name = name,
            num_exercises = num_exercises,
            exercise_names = exercises,
            exercise_sets = sets,
            exercise_reps = reps,
            exercise_weights = weights
        )
        db.session.add(new_workout)
        db.session.commit()
        return jsonify({
            "workout_creation_message": "Workout creation successful"
        }), 201
    except Exception as e:
        logger.debug(f"Error creating workout: {e}")
        db.session.rollback()
        return jsonify({
            "workout_creation_message": "Sorry, an error occurred. Please try again."
        }), 500
    
@workoutbp.route('/getworkout')
@login_required
def get_workout():
    logger.info("Get workout called ...")
    logger.info(g.user.id)
    #For now just give them the only workout they ever created. Add date functionality later:
    workout = Workout.query.filter_by(user_id=g.user.id).first()
    logger.info(f"WORKOUT QUERY PERFORMED. WORKOUT SELECTED: {workout}")
    
    try:
        if workout:
            return jsonify({
                "home_display_message": f"TODAY'S WORKOUT: {workout.workout_name}",
                "name": workout.workout_name,
                "num_exercises": workout.num_exercises,
                "exercises": workout.exercise_names,
                "sets": workout.exercise_sets,
                "reps": workout.exercise_reps,
                "weights": workout.exercise_weights
            }), 200
        else:
            logger.info("/GETWORKOUT ERROR 404. WORKOUT DOES NOT EXIST")
            return jsonify({"home_display_message": "You don't have a workout plan set yet!"}), 404
    except Exception as e:
        logger.debug(f"Error getting workout: {e}")
        db.session.rollback()
        return jsonify({
            "home_display_message": "Unknown error. Please reload and try again."
        }), 500