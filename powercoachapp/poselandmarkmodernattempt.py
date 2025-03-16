#AI algorithm for powerjudge
#Pose estimation gets the pose keypoints:
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from mediapipe.framework.formats import landmark_pb2

#Defining the function for formatting the result_callback:
def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    if result.pose_landmarks:
        print("RESULT:")
        print(result.pose_landmarks[0])
        print("RESULT^")
        # Extract pose landmarks from the result
        # Draw landmarks on the frame
        normalizedlandmarks = landmark_pb2.NormalizedLandmarkList()
        for i in result.pose_landmarks[0]:
            normalizedlandmark = landmark_pb2.NormalizedLandmark()
            normalizedlandmark.x = i.x
            normalizedlandmark.y = i.y
            normalizedlandmark.z = i.z
            normalizedlandmark.visibility = i.visibility
            normalizedlandmark.presence = i.presence
            
            normalizedlandmarks = normalizedlandmarks.landmark.add().CopyFrom(normalizedlandmark)
        #normalizedlandmarks = result.pose_landmarks
        #normalizedlandmarks = mp.calculators.core.constant_side_packet_calculator_pb2.mediapipe_dot_framework_dot_formats_dot_landmark__pb2.NormalizedLandmarkList(result.pose_landmarks[0])
        mp_drawing.draw_landmarks(
            frame,                           # The frame to draw landmarks on
            normalizedlandmarks,                  # The pose landmarks
            mp_pose.POSE_CONNECTIONS         # Optional: connections between landmarks
        )

#BaseOptions is a class that creates configuration objects to specify properties needed to run the model. baseoptions is the object here specifying it to be the poselandmarker lite mode.
baseoptions = BaseOptions(model_asset_path='/Users/brian/Documents/Python/PowerCoach/models/pose_landmarker_lite.task')
options = PoseLandmarkerOptions(
    base_options = baseoptions,
    running_mode = RunningMode.LIVE_STREAM,
    num_poses = 1,
    min_pose_detection_confidence = 0.5,
    min_pose_presence_confidence = 0.5,
    min_tracking_confidence = 0.5,
    output_segmentation_masks = False,
    result_callback = result_format
)
poselandmarker = PoseLandmarker.create_from_options(options)

# LIVE STREAM INPUT:
# Use OpenCV’s VideoCapture to start capturing from the webcam.
import cv2 as cv
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Create a loop to read the latest frame from the camera using VideoCapture
start_time = time.time()
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    #cv.imshow('mpframe', frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) #NumPy array data type
    mpframe = mp.Image(mp.ImageFormat.SRGB, frame) #MediaPipe Image data type
    
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - start_time) * 1000)
    pose = poselandmarker.detect_async(mpframe, frame_timestamp_ms)
    print('success after detect_async')
    
    # https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/pose_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Pose_Landmarker.ipynb
    
    cv.imshow('Pose Frames', cv.cvtColor(frame, cv.COLOR_RGB2BGR))
    
    if cv.waitKey(1) == ord('q'):
        break
cap.release()
cv.destroyAllWindows()
    
#This just instantiates the structure of the output of the pose landmarker model before it puts it out. No need for that here, unless you want it for future reference:    
"""
    result = PoseLandmarkerResult(
        pose_landmarks: List[List[landmark_module.NormalizedLandmark]],
        pose_world_landmarks: List[List[landmark_module.Landmark]],
        segmentation_masks: Optional[List[image_module.Image]] = None
    )
"""

#Hueristic model to make the corrections --> quick, rule-based feedback (transition to more powerful supervised machine learning model after this works)