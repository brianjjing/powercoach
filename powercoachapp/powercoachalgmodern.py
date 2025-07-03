import os, time, base64
import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from mediapipe.framework.formats import landmark_pb2
from powercoachapp.bbelldetectioncreator import bbell_detector_model, barbell_bounding_box
from powercoachapp.exercises.deadlift import start
from powercoachapp.extensions import logger

start_time = None
mpframe = None
message = None

#JUST THE FORMAT. EVENTUALLY YOU'LL JUST HAVE EVERY DIFFERENT EXERCISE BE A DIFFERENT FILE.
def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global start_time, message
    #replace all returns with emit()
    if result.pose_landmarks:
        logger.debug("The pose landmarks exist")
        timestamp_ms = int((time.time() - start_time) * 1000)
        bbell_detector_model.detect_async(mpframe, timestamp_ms)
        
        if barbell_bounding_box: #is this enough to show that there is a barbell???
            logger.debug("Barbell in frame too")
            message = start(result.pose_landmarks, barbell_bounding_box) #should rescale the bounding box to be original dimensions
        else:
            logger.debug("But barbell not in frame")
            message = 'Barbell not in frame'
    else:
        logger.debug("Pose landmarks dont exist")
        message = 'Make your whole body clearly visible in the frame'
        #landmark_pb2.NormalizedLandmarkList(), landmark_pb2.NormalizedLandmark()

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

# Create a loop to read the latest frame from the camera using VideoCapture
def powercoachalg(base64string):
    
    global start_time, mpframe, message
    
    bytes_frame = base64.b64decode(base64string)

    numpy_frame = np.frombuffer(bytes_frame, np.uint8)

    cv_frame = cv.imdecode(numpy_frame, cv.IMREAD_COLOR)

    if cv_frame is None:
        logger.debug("Could not decode the image from Base64 string.")
        return "Could not decode the image from Base64 string."

    cv_frame_rgb = cv.cvtColor(cv_frame, cv.COLOR_BGR2RGB)

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - start_time) * 1000)
    poselandmarker.detect_async(mpframe, frame_timestamp_ms)
    
    logger.debug('frame success')
    
    return message

#powercoachalg()