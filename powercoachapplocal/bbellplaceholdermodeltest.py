import os, time, base64
import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker,   PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from powercoachapplocal.bbellplaceholdermodel import bar_detector_model
from powercoachapplocal.extensions import shared_data
from powercoachapplocal.exercises.deadlift import start_test

#For computer use:
# def message_format():
#     h, w = shared_data['original_frame'].shape[:2]
    
#     text = shared_data['message']
#     font = cv.FONT_HERSHEY_SIMPLEX
#     font_scale = 2.5
#     thickness = 5

#     # Get text size
#     (text_w, text_h), baseline = cv.getTextSize(text, font, font_scale, thickness)

#     # Position to center the text at the top
#     x = (w - text_w) // 2
#     y = 100  # pixels from the top

#     # Background rectangle coordinates
#     rect_x1 = x - 50
#     rect_y1 = y - text_h - 50
#     rect_x2 = x + text_w + 50
#     rect_y2 = y + baseline + 50

#     # Draw filled rectangle (highlight)
#     cv.rectangle(shared_data['original_frame'], (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)

#     # Draw text on top (black)
#     cv.putText(shared_data['original_frame'], text, (x, y), font, font_scale, (0, 0, 0), thickness, lineType=cv.LINE_AA)

def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    #Should run all this in a background thread:
    if result.pose_landmarks and shared_data['bar_bbox']:
        start_test(result.pose_landmarks[0], shared_data['bar_bbox'], shared_data['deadlift_stage'])
        print(shared_data['bar_bbox'])
    #message_format()

#BaseOptions is a class that creates configuration objects to specify properties needed to run the model. baseoptions is the object here specifying it to be the poselandmarker lite mode.
baseoptions = BaseOptions(model_asset_path=os.path.join(os.path.dirname(__file__), 'models', 'pose_landmarker_lite.task'))
options = PoseLandmarkerOptions(
    base_options = baseoptions,
    running_mode = RunningMode.LIVE_STREAM,
    num_poses = 1,
    min_pose_detection_confidence = 0.5,
    min_pose_presence_confidence = 0.5,
    min_tracking_confidence = 0.5,
    output_segmentation_masks = False,
    result_callback = result_format #basically the result_listener
)
poselandmarker = PoseLandmarker.create_from_options(options)

#FOR TESTING WITH A SWIFT FRONTEND, BUT HOSTING ON COMPUTER:
def powercoachalg(jpegData):
    numpy_frame = np.frombuffer(jpegData, np.uint8)
    print("Converted jpeg data to numpy frame")

    cv_frame_rgb = cv.cvtColor(cv.imdecode(numpy_frame, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
    print("Decompressed to RGB cv frame")

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    print("Converted to mediapipe frame")
    
    shared_data['original_frame'] = cv_frame_rgb
    shared_data['frame_height'] = cv_frame_rgb.shape[0]
    shared_data['frame_width'] = cv_frame_rgb.shape[1]
    
    frame_timestamp_ms = int((time.time() - shared_data['start_time']) * 1000)
    
    bar_detector_model.detect_async(mpframe, frame_timestamp_ms)
    print("bbell detection model running ...")
    poselandmarker.detect_async(mpframe, frame_timestamp_ms) #After barbell is detected. Then THIS is where you do it, since all the variables are in this file.
    print("pose landmarker model running ...")
    time.sleep(0.03)

#FOR TESTING ON THE COMPUTER'S CAMERA:
# def powercoachalg():
#     shared_data['original_frame'] = None
#     shared_data['message'] = 'BARBELL NOT IN FRAME'
#     shared_data['bar_bbox'] = None
#     shared_data['deadlift_stage'] = 1
    
#     cap = cv.VideoCapture(0)  # Open default camera
#     start_time = time.time()
    
#     while cap.isOpened():
#         ret, frame = cap.read()
#         shared_data['original_frame'] = frame
#         shared_data['frame_height'] = frame.shape[0]
#         shared_data['frame_width'] = frame.shape[1]
#         if not ret:
#             print("Failed to grab frame")
#             break

#         # Convert BGR to RGB
#         frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#         mpframe = mp.Image(mp.ImageFormat.SRGB, data=frame_rgb)

#         # Calculate timestamp in milliseconds
#         frame_timestamp_ms = int((time.time() - start_time) * 1000)

#         # Detect asynchronously (make sure you have a callback set in options or handle results otherwise)
#         bar_detector_model.detect_async(mpframe, frame_timestamp_ms)
#         poselandmarker.detect_async(mpframe, frame_timestamp_ms) #After barbell is detected. Then THIS is where you do it, since all the variables are in this file.
#         time.sleep(0.05) #To avoid the overflow - will not show up as laggy once you have the camera view

        
#         # Optional: visualize landmarks or detections here if you have a synchronous interface or cached results
#         # For demonstration, we just show the camera frame
#         cv.imshow("Camera", shared_data['original_frame'])

#         if cv.waitKey(1) & 0xFF == ord('q'):
#             break

#powercoachalg()