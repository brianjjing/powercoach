import os, time, base64
import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from powercoachapp.bbelldetectionplaceholdermodel import bbell_detection_model
from powercoachapp.exercises.barbell import deadlift
from powercoachapp.extensions import logger, shared_data

#JUST THE FORMAT. EVENTUALLY YOU'LL JUST HAVE EVERY DIFFERENT EXERCISE BE A DIFFERENT FILE.
def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    logger.info("Pose landmarker result achieved, deadlift running ...")
    if result.pose_landmarks and shared_data['bar_bbox']:
        deadlift(result.pose_landmarks[0], shared_data['bar_bbox'], shared_data['deadlift_stage'])
        logger.info('Deadlift alg ran.')

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
def powercoachalg(jpegData):
    numpy_frame = np.frombuffer(jpegData, np.uint8)
    logger.info("Converted jpeg data to numpy frame")
    
    cv_frame_rgb = cv.cvtColor(cv.imdecode(numpy_frame, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
    logger.info("Decompressed to RGB cv_frame")

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    logger.info("Converted to mediapipe frame")
    
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - shared_data['start_time']) * 1000)
    
    bbell_detection_model.detect_async(mpframe, frame_timestamp_ms)
    logger.info("bbell detection model running ...")
    poselandmarker.detect_async(mpframe, frame_timestamp_ms)
    logger.info("pose landmarker model running ...")
    #Will use bbelldetectionmodel later, for now using regular object detection as placeholder:
    #bbelldetectionmodel.detect_async(mpframe, frame_timestamp_ms)