#AI algorithm for powerjudge
#Pose estimation gets the pose keypoints:
import os, time
import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from mediapipe.framework.formats import landmark_pb2
from powercoachapp.bbelldetectionbbox import printresultbbox, livebbelldetection
from powercoachapp.exercises.deadlift import start
from powercoachapp.extensions import logger, handler, socketio

start_time = None
mpframe = None

#USING THE OPENCV VERSION:

#JUST THE FORMAT. EVENTUALLY YOU'LL JUST HAVE EVERY DIFFERENT EXERCISE BE A DIFFERENT FILE.
def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global start_time
    #replace all returns with emit()
    if result.pose_landmarks:
        logger.debug("The pose landmarks exist")
        timestamp_ms = int((time.time() - start_time) * 1000)
        livebbelldetection.detect_async(mpframe, timestamp_ms)
        
        if printresultbbox: #is this enough to show that there is a barbell???
            logger.debug("Barbell in frame too")
            #WILL DO:
            message = start(result.pose_landmarks, printresultbbox) #should rescale the bounding box to be original dimensions
            #socketio.emit('powercoach_message', message)
            #also once done, make this in just the deadlift file.
        else:
            logger.debug("But barbell not in frame")
            #socketio.emit('powercoach_message', 'Barbell not in frame')
    else:
        logger.debug("Pose landmarks dont exist")
        #socketio.emit('powercoach_message', 'Make your whole body clearly visible in the frame')
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

#WITH WEBSOCKETS:
#base64 --> bytes --> numpy --> mediapipe

# Create a loop to read the latest frame from the camera using VideoCapture
def powercoachalg():
    global start_time
    
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
        global mpframe
        mpframe = mp.Image(mp.ImageFormat.SRGB, frame) #MediaPipe Image data type
        
        #Detecting poses from the image:
        frame_timestamp_ms = int((time.time() - start_time) * 1000)
        poselandmarker.detect_async(mpframe, frame_timestamp_ms)
        
        logger.debug('frame success')
        
        cv.imshow('Pose Frames', cv.cvtColor(frame, cv.COLOR_RGB2BGR))
        
        if cv.waitKey(1) == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()

powercoachalg()

#This just instantiates the structure of the output of the pose landmarker model before it puts it out. No need for that here, unless you want it for future reference:    
"""
    result = PoseLandmarkerResult(
        pose_landmarks: List[List[landmark_module.NormalizedLandmark]],
        pose_world_landmarks: List[List[landmark_module.Landmark]],
        segmentation_masks: Optional[List[image_module.Image]] = None
    )
"""