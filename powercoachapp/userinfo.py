from datetime import date
from flask import Blueprint, g, request, jsonify
from powercoachapp.auth import login_required
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import Workout

# workoutbp = Blueprint('workouts', __name__, url_prefix='/workouts')

# #Workout Creation Route:
# @workoutbp.route('/createworkout', methods=['POST'])
# @login_required
# def set_user_data():