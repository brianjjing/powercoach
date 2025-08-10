from datetime import date
from flask import Blueprint, g, request, jsonify
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import Workout

workoutbp = Blueprint('workouts', __name__, url_prefix='/workouts')

#Workout Creation Route:
@workoutbp.route('/createworkout', methods=['POST'])
@login_required
def create_workout():
    workout_data = request.get_json()
    
    if not workout_data:
        return jsonify({"workout_creation_message": "Please enter at least one exercise!"}), 400
    
    #All lists:
    name = workout_data['name']
    exercises = workout_data['exercises'] #Will be limited to nothing, or a whole list of exercises.
    sets = workout_data['sets']
    reps = workout_data['reps']
    weights = workout_data['weights']
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
    
    for exercise_index in num_exercises:
        if not exercises[exercise_index]:
            return jsonify({'workout_creation_message': 'Exercise name is required.', 'index': exercise_index}), 400
        elif not sets[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of sets is required.', 'index': exercise_index}), 400
        elif not reps[exercise_index]:
            return jsonify({'workout_creation_message': 'Number of reps is required.', 'index': exercise_index}), 400
        elif not weights[exercise_index]:
            return jsonify({'workout_creation_message': 'Exercise weight is required.', 'index': exercise_index}), 400
        elif not every_blank_days[exercise_index]:
            return jsonify({'workout_creation_message': 'Workout frequency is required', 'index': exercise_index}), 400
    
    try:
        new_workout = Workout(
            user_id = g.user.id,
            workout_name = name,
            num_exercises = num_exercises,
            exercise_names = exercises,
            exercise_sets = sets,
            exercise_reps = reps,
            exercise_weights = weights,
            completed = [False for _ in num_exercises],
            start_day = date.today(),
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
    today = date.today()
    
    user_workouts = Workout.query.filter_by(user_id=g.user.id).all()
    
    try:
        if user_workouts:
            todays_workouts = []
            other_workouts = []
            
            #Getting today's workouts and the other workouts
            for workout in user_workouts:
                logger.info("Today: ", today)
                logger.info("Workout start day: ", workout.start_day)
                logger.info("Int difference: ", (today - workout.start_day).days)
                logger.info(type((today - workout.start_day).days))
                logger.info("Every blank days: ", workout.every_blank_days)
                logger.info(type(workout.every_blank_days))
                if ((today - workout.start_day).days % workout.every_blank_days) == 0:
                    todays_workouts.append({
                        "workout_id": workout.workout_id,
                        "name": workout.workout_name,
                        "num_exercises": workout.num_exercises,
                        "exercises": workout.exercise_names,
                        "sets": workout.exercise_sets,
                        "reps": workout.exercise_reps,
                        "weights": workout.exercise_weights,
                        "completed": workout.completed,
                        "every_blank_days": workout.every_blank_days
                    })
                else:
                    other_workouts.append({
                        "workout_id": workout.workout_id,
                        "name": workout.workout_name,
                        "num_exercises": workout.num_exercises,
                        "exercises": workout.exercise_names,
                        "sets": workout.exercise_sets,
                        "reps": workout.exercise_reps,
                        "weights": workout.exercise_weights,
                        "completed": workout.completed,
                        "every_blank_days": workout.every_blank_days
                    })
            logger.info(f"WORKOUT QUERY PERFORMED")
            logger.info(f"Today's workouts: {todays_workouts}")
            logger.info(f"Other workouts: {other_workouts}")
            
            if not todays_workouts:
                logger.info("Today's workout does not exist but other_workouts does.")
                return jsonify({
                    "home_display_message": "You don't have a workout planned for today!",
                    "todays_workouts": [],
                    "other_workouts": other_workouts
                }), 200
                
            #Else:
            return jsonify({
                "home_display_message": f"TODAY'S WORKOUT:\n{user_workouts[0].workout_name}", # Get the first workout name
                "todays_workouts": todays_workouts,
                "other_workouts": other_workouts
            }), 200
        else:
            logger.info("No workouts exist")
            return jsonify({
                "home_display_message": "You don't have a workout planned for today!",
                "todays_workouts": [],
                "other_workouts": []}), 200
    except Exception as e:
        logger.info(f"Error getting workout: {e}")
        return jsonify({
            "home_display_message": "Unknown error. Please reload and try again."
        }), 500
        
@workoutbp.route('/markexercisedone', methods=['POST'])
@login_required
def mark_exercise_done():
    finished_exercise = request.get_json()
    
    if not finished_exercise:
        return jsonify({"exercise_finished_message": "Error marking the exercise as complete."}), 400