from zoneinfo import ZoneInfo
from datetime import datetime
from flask import Blueprint, g, request, jsonify
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger, shared_data
from powercoachapp.sqlmodels import Workout
from powercoachapp.exercises.barbell import barbell_exercises

workoutbp = Blueprint('workouts', __name__, url_prefix='/workouts')

#Workout Creation Route:
@workoutbp.route('/createworkout', methods=['POST'])
@login_required
def create_workout():
    workout_data = request.get_json()
    
    if not workout_data:
        return jsonify({"workout_creation_message": "Please enter at least one exercise!"}), 400
    
    logger.info(workout_data)
    
    #All lists:
    name = workout_data['name']
    exercises = workout_data['exercises'] #Will be limited to nothing, or a whole list of exercises.
    sets = workout_data['sets']
    reps = workout_data['reps']
    num_exercises = len(exercises)
    every_blank_days = workout_data['every_blank_days']
    
    if not name:
        return jsonify({
            "workout_creation_message": f"Write a name for your workout!"
        }), 400
    if not exercises:
        return jsonify({"workout_creation_message": "Please enter at least one exercise!"}), 400
    if Workout.query.filter_by(user_id=g.user.id, workout_name=name).first():
        return jsonify({
            "workout_creation_message": f"You already have a workout called {name}!"
        }), 409
    if len(set(exercises)) != len(exercises):
        return jsonify({"workout_creation_message": "No repeating exercises in a workout!"}), 400
    
    existing_workout = Workout.query.filter_by(user_id=g.user.id).first()
    if existing_workout and (existing_workout.every_blank_days != every_blank_days):
        return jsonify({
            "workout_creation_message": f"All workout plans must have the same frequency! You are attempting to add a workout every {every_blank_days} days when your other workout plans are every {existing_workout.every_blank_days} days."
        }), 400
    
    for exercise_index in range(num_exercises):
        if not exercises[exercise_index]:
            return jsonify({'workout_creation_message': 'Exercise name is required.', 'index': exercise_index}), 400
        elif not sets[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of sets is required.', 'index': exercise_index}), 400
        elif not reps[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of reps is required.', 'index': exercise_index}), 400
    if not every_blank_days:
        return jsonify({'workout_creation_message': 'Workout frequency is required', 'index': exercise_index}), 400
    
    try:
        new_workout = Workout(
            user_id = g.user.id,
            workout_name = name,
            exercise_names = exercises,
            exercise_sets = sets,
            exercise_reps = reps,
            completed = [False for _ in exercises],
            start_datetime = datetime.now().astimezone(ZoneInfo('UTC')),
            every_blank_days = every_blank_days
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
    
@workoutbp.route('/getworkouts')
@login_required
def get_workouts():
    logger.info("Get workout called ...")
    logger.info(g.user.id)
    
    user_workouts = Workout.query.filter_by(user_id=g.user.id).all()
    
    try:
        client_timezone_str = request.args.get('timezone', 'GMT')
        current_datetime_tz = datetime.now().astimezone(ZoneInfo(client_timezone_str))
        today = current_datetime_tz.date()
        
        if user_workouts:
            workouts = []
            
            #Getting today's workouts and the other workouts
            for workout in user_workouts:
                
                workout_start_datetime_client_tz = workout.start_datetime.astimezone(ZoneInfo(client_timezone_str))
                workout_start_date = workout_start_datetime_client_tz.date()
                is_workout_today = lambda: True if (((today - workout_start_date).days % workout.every_blank_days) == 0) else False
                
                #Get the client's timezone from the request query parameters.
                #Get today's date in the client timezone, and convert start date to client timezone (from UTC which it is stored as).
                #Now compare the dates for real.                
                logger.info(f"Today: {today}")
                logger.info(f"Workout start day: {workout_start_date}")
                logger.info(f"Int difference: {(today - workout_start_date).days}")
                logger.info(type((today - workout_start_date).days))
                logger.info(f"Every blank days: {workout.every_blank_days}")
                logger.info(type(workout.every_blank_days))
                
                workouts.append({
                    "workout_id": workout.workout_id,
                    "name": workout.workout_name,
                    "exercises": workout.exercise_names,
                    "sets": workout.exercise_sets,
                    "reps": workout.exercise_reps,
                    "completed": workout.completed,
                    "every_blank_days": workout.every_blank_days,
                    "today": is_workout_today()
                })
                
            logger.info(f"WORKOUT QUERY PERFORMED")
            logger.info(f"Workouts: {workouts}")
            
            
            if not workouts:
                logger.info("Workouts were found for the user")
                return jsonify({
                    "home_display_message": "You don't have a workout planned for today!",
                    "workouts": workouts
                }), 200
            #Else:
            return jsonify({ #Should be 
                        "home_display_message": f"TODAY'S WORKOUT:\n{workouts[0]['name']}",
                        "workouts": workouts
                    }), 200
        else:
            logger.info("No workouts exist")
            return jsonify({
                "home_display_message": "You don't have a workout planned for today!",
                "workouts": workouts}), 200
    except Exception as e:
        logger.info(f"Error getting workout: {e}")
        return jsonify({
            "home_display_message": "Unknown error. Please reload and try again."
        }), 500

@workoutbp.route('/deleteworkout', methods=['POST'])
@login_required
def delete_workout():
    workout_data = request.get_json()
    
    try:
        workout_id = workout_data['workout_id']
        if not workout_id:
            return jsonify({"workout_deletion_message": "Workout id not found!"}), 400
    except Exception as e:
        logger.info(f"Error decoding the workout id: {e}")
        return jsonify({"workout_deletion_message": "Error decoding the workout id."}), 500
    logger.info(workout_id)
    
    try:
        # Find the workout by its primary key
        workout_to_delete = Workout.query.get(workout_id)

        if not workout_to_delete:
            return jsonify({"workout_deletion_message": "Workout not found."}), 404

        # Authorization check: Ensure the user owns the workout
        if workout_to_delete.user_id != g.user.id:
            return jsonify({"workout_deletion_message": "You are not authorized to delete this workout."}), 403

        # Delete the workout from the session
        db.session.delete(workout_to_delete)
        db.session.commit()
        
        return jsonify({
            "workout_deletion_message": "Workout deletion successful"
        }), 200
    except Exception as e:
        logger.debug(f"Error deleting workout: {e}")
        db.session.rollback()
        return jsonify({
            "workout_deletion_message": "Sorry, an error occurred. Please try again."
        }), 500

@workoutbp.route('/markexercisedone', methods=['POST'])
@login_required
def mark_exercise_done():
    finished_exercise = request.get_json()
    
    if not finished_exercise:
        return jsonify({"exercise_finished_message": "Error marking the exercise as complete."}), 400