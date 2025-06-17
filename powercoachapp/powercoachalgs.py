#ALGORITHM IMPORTS:
import cv2
import mediapipe as mp
import numpy as np
import base64
import json
from flask import jsonify, Response
import time
from powercoachapp.bbelldetectionbbox import printresultbbox
from powercoachapp.exercises.deadlift import start
from powercoachapp.extensions import logger

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

active_clients = set()

#POWERCOACH WITH FRAME FROM AVCAPTURESESSION.OUTPUT:
def powercoachalg(base64_string):
    logger.info("powercoach algorithm is starting")
    with mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.8, min_tracking_confidence=0.8) as pose:
        #UNDERSTAND THE IMAGE TYPE CONVERSION:
        # Step 1: Decode the Base64 string to raw JPEG bytes
        jpg_bytes = base64.b64decode(base64_string)
        logger.info("decoded to jpg bytes")

        # Step 2: Convert bytes to a 1D NumPy array
        jpg_array = np.frombuffer(jpg_bytes, dtype=np.uint8)
        logger.info("made into jpg array")

        # Step 3: Decode JPEG to BGR image (OpenCV default)
        bgr_image = cv2.imdecode(jpg_array, cv2.IMREAD_COLOR)
        logger.info("decoded into a cv2 bgr image")

        if bgr_image is None:
            logger.info("Error: Could not decode image")
            return "Error: Could not decode image"

        # Step 4: Convert BGR to RGB (required for MediaPipe)
        rgb_frame = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        logger.info("made into rbg image")

        # Process the frame to detect pose
        results = pose.process(rgb_frame)
        logger.info("pose detection applied")

        # Draw the pose landmarks on the frame:
        """if results.pose_landmarks:
            #print(results.pose_landmarks)
            mp_drawing.draw_landmarks(
                frame,  # Original BGR frame
                results.pose_landmarks,  # Detected landmarks
                mp_pose.POSE_CONNECTIONS  # Connections between landmarks
            )"""
        if results.pose_landmarks:
            logger.info("the pose landmarks exist")
            if printresultbbox:
                logger.info("barbell in frame too")
                return start(results.pose_landmarks, printresultbbox)
            else:
                logger.info("Barbell not in frame")
                return 'Barbell not in frame'
        else:
            logger.info("pose landmarks dont exist")
            return 'Make your whole body clearly visible in the frame'
        
        # COMPUTER BACKEND TESTING: Display the frame
        #yield (b'--frame\r\n'
            #b'Content-Type: image/jpeg\r\n\r\n' + bytesframe + b'\r\n')

#POWERCOACH WITH OPENCV FRAME:
# def powercoachalg(sid):
#     print("powercoach algorithm is starting")
#     cap = cv2.VideoCapture(0)  # 0 for default webcam
#     if not cap.isOpened():
#         print("Error: Could not open webcam.")
#         exit()
#     try:
#         with mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.8, min_tracking_confidence=0.8) as pose:
#             while sid in active_clients:
#                 ret, frame = cap.read()
#                 if not ret:
#                     print("Failed to grab frame. Exiting...")
#                     break
                
#                 encoderet, encodedjpg = cv2.imencode('.jpg', frame)
#                 if not encoderet:
#                     print("Could not encode as a .jpg. Exiting...")
#                     break
#                 bytesframe = encodedjpg.tobytes()
#                 base64frame = base64.b64encode(bytesframe).decode('utf-8')
#                 json_frame = json.dumps({
#                     'json_data': base64frame
#                 })
                
#                 # Convert the BGR frame to RGB for MediaPipe
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 # Process the frame to detect pose
#                 results = pose.process(rgb_frame)

#                 # Draw the pose landmarks on the frame:
#                 """if results.pose_landmarks:
#                     #print(results.pose_landmarks)
#                     mp_drawing.draw_landmarks(
#                         frame,  # Original BGR frame
#                         results.pose_landmarks,  # Detected landmarks
#                         mp_pose.POSE_CONNECTIONS  # Connections between landmarks
#                     )"""
#                 if results.pose_landmarks:
#                     if printresultbbox:
#                         yield start(results.pose_landmarks, printresultbbox)
#                     else:
#                         yield 'Barbell not in frame'
#                 else:
#                     yield 'Make your whole body clearly visible in the frame'
                
#                 # COMPUTER BACKEND TESTING: Display the frame
#                 #yield (b'--frame\r\n'
#                     #b'Content-Type: image/jpeg\r\n\r\n' + bytesframe + b'\r\n')
#     except Exception as e:
#         print(f'Error: {e}')
#     finally:
#         cap.release()
#         print('Camera released')

#['LEFT_ANKLE', 'LEFT_EAR', 'LEFT_ELBOW', 'LEFT_EYE', 'LEFT_EYE_INNER', 'LEFT_EYE_OUTER', 'LEFT_FOOT_INDEX', 'LEFT_HEEL', 'LEFT_HIP',
#'LEFT_INDEX', 'LEFT_KNEE', 'LEFT_PINKY', 'LEFT_SHOULDER', 'LEFT_THUMB', 'LEFT_WRIST', 'MOUTH_LEFT', 'MOUTH_RIGHT', 'NOSE', 
#'RIGHT_ANKLE', 'RIGHT_EAR', 'RIGHT_ELBOW', 'RIGHT_EYE', 'RIGHT_EYE_INNER', 'RIGHT_EYE_OUTER', 'RIGHT_FOOT_INDEX', 'RIGHT_HEEL', 
#'RIGHT_HIP', 'RIGHT_INDEX', 'RIGHT_KNEE', 'RIGHT_PINKY', 'RIGHT_SHOULDER', 'RIGHT_THUMB', 'RIGHT_WRIST']

def drawlandmarks(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pose = mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.8, min_tracking_confidence=0.8)
    results = pose.process(image)
    if results.pose_landmarks:
        #print(results.pose_landmarks)
        mp_drawing.draw_landmarks(
            image,  # Original BGR frame
            results.pose_landmarks,  # Detected landmarks
            mp_pose.POSE_CONNECTIONS  # Connections between landmarks
        )
        cv2.imshow('Pose Estimation', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return
    else:
        return "Error: No landmarks detected"
    
#drawlandmarks('/Users/brian/Downloads/DEADY8.jpeg')