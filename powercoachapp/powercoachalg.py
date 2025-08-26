import os, time
import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from powercoachapp.bbelldetectioncreatemodel import bbell_detector_model
import powercoachapp.exercises.barbell as barbell
from powercoachapp.extensions import logger, shared_data

def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    logger.info("Pose landmarker result achieved, deadlift running ...")
    if result.pose_landmarks and shared_data['bar_bbox']:
        #Eventually you need to handle the case of different equipment types too.
        exercise_alg = barbell.barbell_exercises[shared_data['exercise']]
        #Only detect the straight barbells close to the camera, to enforce that only frames with barbell directly in front will be reviewed.
        message = exercise_alg(result.pose_landmarks[0], shared_data['bar_bbox'], shared_data['lift_stage'])
        shared_data['message'] = message
        logger.info('Deadlift alg ran.')

baseoptions = BaseOptions(model_asset_path=os.path.join(os.path.dirname(__file__), 'models', 'pose_landmarker_lite.task'))
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

def powercoachalg(jpegData):
    numpy_frame = np.frombuffer(jpegData, np.uint8)
    logger.info("Converted jpeg data to numpy frame")
    
    cv_frame_rgb = cv.cvtColor(cv.imdecode(numpy_frame, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
    logger.info("Decompressed to RGB cv_frame")
    shared_data['frame_height'] = cv_frame_rgb.shape[0]
    shared_data['frame_width'] = cv_frame_rgb.shape[1]

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    logger.info("Converted to mediapipe frame")
        
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - shared_data['start_time']) * 1000)
    
    bbell_detector_model.detect_async(mpframe, frame_timestamp_ms)
    logger.info("bbell detection model running ...")
    poselandmarker.detect_async(mpframe, frame_timestamp_ms)
    logger.info("pose landmarker model running ...")