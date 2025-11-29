from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging, sys
import mediapipe as mp

mp_pose = mp.solutions.pose
mplandmarks = mp.solutions.pose.PoseLandmark

socketio = SocketIO()

clients = set()
login_manager = LoginManager()
db = SQLAlchemy()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)

#Sliding window data:
sliding_window_framework_metadata = {
    'WINDOW_LEN': 4,          # SEQUENCE LENGTH: Set to 4 frames for low latency testing
    'N_MOTION_CLASSES': 2,
    'N_FEATURES': 10,         # Total number of kinematic features (Input size for both models)
    'N_HMM_STATES': 5,        # 0: Setup, 1: Eccentric, 2: Concentric, 3: Lockout, 4: Stretch
    'N_FAULT_CLASSES': 2,     # 0: No Clapping, 1: Clapping Motion ==> Will DEFINITELY be more.
    'MODEL_WEICHTS_PATH': 'clapping_cnn_weights.h5',
    'HOP_SIZE': 2,
    'DEVICE': 'CPU',          
    'CONFIDENCE_THRESHOLD': 0.8
}

active_form_correctors = {}

left_thumb = poselandmarks[mp_pose.PoseLandmark.LEFT_THUMB]
right_thumb = poselandmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
left_shoulder = poselandmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
right_shoulder = poselandmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
left_ankle = poselandmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
right_ankle = poselandmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

left_hip = poselandmarks[mp_pose.PoseLandmark.LEFT_HIP]
right_hip = poselandmarks[mp_pose.PoseLandmark.RIGHT_HIP]
left_knee = poselandmarks[mp_pose.PoseLandmark.LEFT_KNEE]
right_knee = poselandmarks[mp_pose.PoseLandmark.RIGHT_KNEE]

left_elbow = poselandmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
right_elbow = poselandmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
left_wrist = poselandmarks[mp_pose.PoseLandmark.LEFT_WRIST]
right_wrist = poselandmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

nose = poselandmarks[mp_pose.PoseLandmark.NOSE]

left_mouth = poselandmarks[mp_pose.PoseLandmark.MOUTH_LEFT]
right_mouth = poselandmarks[mp_pose.PoseLandmark.MOUTH_RIGHT]

left_index = poselandmarks[mp_pose.PoseLandmark.LEFT_INDEX]
right_index = poselandmarks[mp_pose.PoseLandmark.RIGHT_INDEX]

exercise_feature_mapping = {
    'Conventional Deadlifts': [left_thumb, right_thumb, #1. Hands on bar
                               left_shoulder, right_shoulder, left_ankle, right_ankle, #2. Feet shoulder width apart
                               left_hip, right_hip, left_knee, right_knee,#3. Don't round back
                               left_elbow, right_elbow, left_wrist, right_wrist, #4. Arms straight
                               nose], #5. Keep neck neutral
    
    'RDLs': [left_thumb, right_thumb, #1. Hands on bar
             left_shoulder, right_shoulder, left_ankle, right_ankle, #2. Feet shoulder width apart
             left_hip, right_hip, left_knee, right_knee, #3. Don't round back
             left_elbow, right_elbow, left_wrist, right_wrist, #4. Arms straight
             nose #5. Keep neck neutral
             ],
    'Deep Squats': [left_shoulder, right_shoulder, left_ankle, right_ankle, #1. Feet shoulder width apart
                    left_thumb, right_thumb, left_mouth, right_mouth, #2. Get under the bar
                    left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                    #4. No knee cave
                    nose #5. Neck straight
                    ],
    '90-Degree Squats': [left_shoulder, right_shoulder, left_ankle, right_ankle, #1. Feet shoulder width apart
                    left_thumb, right_thumb, left_mouth, right_mouth, #2. Get under the bar
                    left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                    #4. No knee cave
                    nose #5. Neck straight
                    ],
    'Quarter Squats': [left_shoulder, right_shoulder, left_ankle, right_ankle, #1. Feet shoulder width apart
                    left_thumb, right_thumb, left_mouth, right_mouth, #2. Get under the bar
                    left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                    #4. No knee cave
                    nose #5. Neck straight
                    ],
    'Barbell Overhead Presses': [left_thumb, right_thumb, #1. Hands on bar
                                 left_shoulder, right_shoulder, left_ankle, right_ankle, #. Feet shoulder width apart
                                 left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                                 nose, #4. Neck straight
                                 left_elbow, right_elbow #5. Elbow flare
                                ],
    'Barbell Bicep Curls': [left_thumb, right_thumb, #1. Hands on bar
                            left_shoulder, right_shoulder, left_ankle, right_ankle, #Feet shoulder width apart
                            left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                            left_elbow, right_elbow, #4. Don't sway elbow
                            left_wrist, right_wrist, left_index, right_index #5. Wrists straight
                            ],
    'Barbell Rows': [left_thumb, right_thumb, #1. Hands on bar
                     left_shoulder, right_shoulder, left_ankle, right_ankle, #Feet shoulder width apart
                     left_hip, right_hip, left_knee, right_knee, #3. Do not round back
                     nose #4. Keep neck neutral
                     #5. Don't be too straight
                     ]
}