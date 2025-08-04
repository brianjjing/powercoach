from powercoachapp.extensions import db

class User(db.Model): #SQLAlchemy automatically converts to lowercase and pluralizes
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    
class UserBackendData(db.Model):
    __tablename__ = 'user_backend_data' #Dunder references object properties

    user_backend_data_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.Float)
    frame_height = db.Column(db.Integer)
    frame_width = db.Column(db.Integer)
    powercoach_message = db.Column(db.String(255), nullable=False)
    bar_bbox = db.Column(db.ARRAY(db.Float), nullable=False)
    confidence = db.Column(db.Float)
    lift_stage = db.Column(db.String(15), nullable=False) #Only eccentric or concentric
    equipment_type = db.Column(db.String(15), nullable=False)
    exercise = db.Column(db.String(32), nullable=False)
    
class Workout(db.Model):
    __tablename__ = 'workouts'
    
    workout_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_name = db.Column(db.String(64), nullable=False)
    num_exercises = db.Column(db.Integer, db.CheckConstraint('num_exercises<=15'), nullable=False)
    exercise_names = db.Column(db.ARRAY(db.String(64)), nullable=False)
    exercise_sets = db.Column(db.ARRAY(db.Integer), nullable=False)
    exercise_reps = db.Column(db.ARRAY(db.Integer), nullable=False)
    exercise_weights = db.Column(db.ARRAY(db.Integer), nullable=False)