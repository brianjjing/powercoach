import os, time
import cv2 as cv
import numpy as np
import mediapipe as mp
from flask import session
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from powercoachapp.bbelldetectioncreatemodel import create_bbell_detection_model
#^^^Change this to use a deployed model!!!
import powercoachapp.exercises.barbell as barbell
from powercoachapp.extensions import logger, sliding_window_framework_metadata, active_form_correctors

#Tensorflow is declarative (focuses on the result, letting system figure out the "how")
#PyTorch is imperative, focusing on you writing step-by-step instructions.

# Here, use PyTorch since you need the customizability - your implementation w the
# custom deque and the parallel threads are complex to the point where you need to specify
# how they are treated/executed.

import threading
from collections import deque
from hmmlearn import hmm

"""
The section below defines the parallel HMM and Conv1D models.
"""

class SlidingWindowResults:
    """
    Wrapper class that holds the consolidated results of the two worker threads: phase and faults.
    """
    def __init__(self):
        self.phase = None #Possible values: concentric, eccentric, lockout, stretch
        self.fault_probs = None

def extract_frame_features(pose_landmarks, bbell_bbox, frame_height, frame_width):
    #Extract the features!
    return

def run_fault_thread(*args):
    #Perform the inference!
    return

def run_phase_thread(*args):
    #Perform the inference!
    return

def pose_landmark_callback(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    logger.info("Pose landmarker result achieved, firing into the session:")
    #Fire and forget:
    if result.pose_landmarks:
        session['pose_landmarks'] = result.pose_landmarks

class SlidingWindowFormCorrector:
    """
    Defining functions for implementing the sliding window form correction algos:
    The stateless models will be initialized from an online saved path (Conv1D, Yolo/custom obj detector) and others (pose landmarkers, HMM) will be made here from options
    """
    def __init__(self, window_size, n_features, n_hmm_states, n_fault_classes):
        #4 phases, and there will be MANY faults possible - for EACH exercise!
        
        self.window_size = window_size
        self.n_features = n_features
        #^^The angles and positions that will be used within the function. (should define em urself)
        self.sliding_window = deque(maxlen=window_size)
        #^^where new data is pushed into for every process.
        
        self.previous_phase = None #(for hysteresis)
        self.frames_since_last_process = 0
        #^^^Counts the frames since the last window process, for implementing hop steps.
        
        # Initialize models
        self.hmm_model = ... #Get the HMM Model which will be deployed on the cloud!
        self.conv_1d_fault_model = ... #Get the CNN fault detection model which will be deployed on the cloud!
        
        # Two worker threads + their shared result object
        self.phase_thread = None #hmm
        self.fault_thread = None #conv1d
        self.sliding_window_results = SlidingWindowResults()
        
        # Hysteresis and State Management Flags
        self.FAULT_ACTIVE = False
        self.FAULT_THRESHOLD = 0.85     
        self.RECOVERY_THRESHOLD = 0.95  
        self.GOOD_FORM_INDEX = 0        
        self.consecutive_good_frames = 0 
        self.current_message = "Initializing..."
        self.text_color = (0, 255, 0)
        
        baseoptions = BaseOptions(model_asset_path=os.path.join(os.path.dirname(__file__), 'models', 'pose_landmarker_lite.task'))
        options = PoseLandmarkerOptions(
            base_options = baseoptions,
            running_mode = RunningMode.LIVE_STREAM,
            num_poses = 1,
            min_pose_detection_confidence = 0.5,
            min_pose_presence_confidence = 0.5,
            min_tracking_confidence = 0.5,
            output_segmentation_masks = False,
            result_callback = pose_landmark_callback
        )
        self.pose_landmarker = PoseLandmarker.create_from_options(options)
        
        self.bbell_detector_model = create_bbell_detection_model()
        
    def process_frame(self, pose_landmarks, bbell_bbox, frame_height, frame_width, HOP_SIZE):
        # 1. Feature Extraction & Window Update (Fast, runs every frame)
        
        #Results is formatted like: [poselandmarks, bbox]
        new_features = extract_frame_features(pose_landmarks, bbell_bbox, frame_height, frame_width) 
        self.sliding_window.append(new_features) 
        self.frames_since_last_process += 1
        
        # 2. Dealing with previous threads if they are unfinished:
        if (self.phase_thread is not None) and (not self.phase_thread.is_alive()):
            if (self.fault_thread is not None) and (not self.fault_thread.is_alive()):
                #Both threads are finished! We will now set the message as the results:
                if (self.sliding_window_results.phase is not None) and (self.sliding_window_results.fault_probs is not None):
                    #Check out wtf this does:
                    self.update_message(
                        self.sliding_window_results.phase, 
                        np.argmax(self.sliding_window_results.fault_probs), 
                        self.sliding_window_results.fault_probs
                    )
                #And then reset the threads.
                self.phase_thread = None
                self.fault_thread = None

        # 3. Starting new inference when past threads are finished, and window size is met:
        if (self.phase_thread is None) and (self.fault_thread is None):
            if (len(self.buffer) == self.window_size) and (self.frames_since_last_process >= HOP_SIZE):
                self.frames_since_last_process = 0 # Reset hop size counter
                
                # Prepare sliding window data COPIES (Copies are crucial for thread safety!)
                window_data = np.array(self.sliding_window, dtype=np.float32)
                sequence_tensor = np.expand_dims(window_data, axis=0) #Converts to a 3d tensor for PyTorch

                # Start fault_thread Thread
                self.fault_thread = threading.Thread(
                    target=run_fault_thread, #callable object that .run() is called on
                    args=(self.conv_1d_fault_model, sequence_tensor, self.sliding_window_results)
                    #^^arguments to be passed into the target function
                )
                self.fault_thread.start()
                
                # Start phase_thread Thread
                self.phase_thread = threading.Thread(
                    target=run_phase_thread,
                    args=(self.hmm_model, window_data, self.sliding_window_results)
                )
                self.phase_thread.start()                
        
        #Main point of the form corrector is to run update_message like above,
        #and so the following aren't really needed. But just keep the returns for debugging:
        return self.FAULT_ACTIVE, self.previous_phase

    def update_message(self, phase, predicted_fault_index, fault_probabilities):
        """
        Implements the Hysteresis Logic and Phase Transition Messaging.
        """
        FAULT_NAMES = ['No Clapping Detected', 'Clapping Motion'] 
        PHASE_NAMES = {0: "Setup", 1: "Eccentric", 2: "Concentric", 3: "Lockout", 4: "Stretch"}
        
        phase_name = PHASE_NAMES.get(phase, "Setup")
        fault_name = FAULT_NAMES[predicted_fault_index]
        fault_prob = fault_probabilities[predicted_fault_index]

        #State management updates:
        #*CHANGE FROM PRINT TO SENDING MESSAGES:
        if (self.previous_phase is not None) and (self.previous_phase != phase):
            #Phase change
            session['powercoach_message'] = "make a phase change message accordingly"
        self.previous_phase = phase
        
        if (fault_name != 'No Clapping Detected') and (fault_prob >= self.FAULT_THRESHOLD) and (not self.FAULT_ACTIVE):
            #Fault detection
            self.FAULT_ACTIVE = True
            session['powercoach_message'] = f"FAULT DETECTION: {fault_prob:.2f}% certainty"
            self.consecutive_good_frames = 0
        elif self.FAULT_ACTIVE:
            #There already is a fault detected (need a recovery period to get out)
            good_form_prob = fault_probabilities[self.GOOD_FORM_INDEX]
            
            if good_form_prob >= self.RECOVERY_THRESHOLD:
                self.consecutive_good_frames += 1
                # Check for sustained recovery
                if self.consecutive_good_frames >= 4: 
                    self.FAULT_ACTIVE = False
                    session['powercoach_message'] = "now reset the message after fault detection"
                    self.consecutive_good_frames = 0
            else:
                self.consecutive_good_frames = 0 
                
        #Now, based on the FAULT_ACTIVE var set right in the code block above,
        # we either set a fault message or phase change message:
        if self.FAULT_ACTIVE:
            session['powercoach_message'] = f"FAULT: {fault_name}"
            self.text_color = (0, 0, 255) # Red/Blue for active detection
        else:
            session['powercoach_message'] = f"Make a message based on their current phase!"
            self.text_color = (0, 255, 0) # Green for good/base state


def powercoachalg(user_id, jpeg_data):
    numpy_frame = np.frombuffer(jpeg_data, np.uint8)
    logger.info("Converted jpeg data to numpy frame")
    
    cv_frame_rgb = cv.cvtColor(cv.imdecode(numpy_frame, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
    logger.info("Decompressed to RGB cv_frame")
    frame_height = cv_frame_rgb.shape[0]
    frame_width = cv_frame_rgb.shape[1]
    logger.info(f"Frame height: {frame_height} pixels")
    logger.info(f"Frame width: {frame_width} pixels")
    #^^^PRINT THE FRAME_HEIGHT AND FRAME_WIDTH AND MAKE SURE IT STAYED AT 256X256!

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    logger.info("Converted to mediapipe frame")
        
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - session['start_time']) * 1000)
    
    active_form_correctors[user_id].bbell_detector_model.detect_async(mpframe, frame_timestamp_ms) #runs 10x a second
    logger.info("bbell detection model running ...")
    active_form_correctors[user_id].pose_landmarker.detect_async(mpframe, frame_timestamp_ms)
    logger.info("pose landmarker model running ...")
    
    active_form_correctors[user_id].process_frame(session['pose_landmarks'], session['bbell_bbox'], frame_height=frame_height, frame_width=frame_width, HOP_SIZE=sliding_window_framework_metadata['HOP_SIZE'])