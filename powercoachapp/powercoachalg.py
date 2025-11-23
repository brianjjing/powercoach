import os, time
import cv2 as cv
import numpy as np
import mediapipe as mp
from flask import session
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, PoseLandmarkerResult, RunningMode
from powercoachapp.bbelldetectioncreatemodel import bbell_detector_model
#^^^Change this to use a deployed model!!!
import powercoachapp.exercises.barbell as barbell
from powercoachapp.extensions import logger

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

class SlidingWindowFormCorrector:
    """
    Defining functions for implementing the sliding window form correction algos:
    """
    def __init__(self, window_size, n_features, n_hmm_states, n_fault_classes):
        #4 phases, and there will be MANY faults possible - for EACH exercise!
        
        self.window_size = window_size
        self.n_features = n_features
        #The angles and positions that will be used within the function. (should define em urself)
        self.buffer = deque(maxlen=window_size)
        
        self.previous_phase = None #(for hysteresis)
        self.frames_since_last_process = 0
        #^^^Counts the frames since the last window process, for implementing hop steps.
        
        # Initialize models
        self.hmm_model = ... #Get the HMM Model which will be deployed on the cloud!
        self.conv_1d_fault_model = ... #Get the CNN fault detection model which will be deployed on the cloud!
        
        # Initialize Keras predictor
        self.cnn_fault_model.predict(np.random.rand(1, window_size, n_features), verbose=0) #???
        
        # Shared result object for parallel threads
        self.model_results = ModelResults()
        
        # Hysteresis and State Management Flags
        self.FAULT_ACTIVE = False
        self.FAULT_THRESHOLD = 0.85     
        self.RECOVERY_THRESHOLD = 0.95  
        self.GOOD_FORM_INDEX = 0        
        self.consecutive_good_frames = 0 
        self.current_message = "Initializing..."
        self.text_color = (0, 255, 0)
        
    def process_frame(self, results, frame_height, frame_width, HOP_SIZE):
        
        # 1. Feature Extraction & Window Update (Runs on every frame)
        new_features = extract_clapping_features(results, frame_height, frame_width) 
        self.buffer.append(new_features) 
        
        # Increment counter
        # NOTE: Even with HOP_SIZE=1, we use the counter logic for consistency
        self.frame_counter += 1
        
        # Check if buffer is full AND hop condition is met
        if len(self.buffer) == self.window_size and self.frame_counter >= HOP_SIZE: 
            
            self.frame_counter = 0 
            
            # Prepare data for concurrent processing
            window_data = np.array(self.buffer, dtype=np.float32)
            sequence_tensor = np.expand_dims(window_data, axis=0)
            
            # --- START PARALLEL INFERENCE ---

            # 1. HMM Thread (Decodes Phase)
            hmm_thread = threading.Thread(
                target=run_hmm_threaded,
                args=(self.hmm_model, window_data, self.model_results)
            )
            
            # 2. CNN Thread (Predicts Fault)
            cnn_thread = threading.Thread(
                target=run_cnn_threaded,
                args=(self.cnn_fault_model, sequence_tensor, self.model_results)
            )
            
            hmm_thread.start()
            cnn_thread.start()
            
            # CRITICAL: Wait for both threads to finish before processing results
            hmm_thread.join()
            cnn_thread.join()
            
            # --- END PARALLEL INFERENCE ---

            # --- HYSTERESIS & MESSAGE LOGIC (Sequential Control) ---
            
            if self.model_results.phase is not None and self.model_results.fault_probs is not None:
                self.send_message(
                    self.model_results.phase, 
                    np.argmax(self.model_results.fault_probs), 
                    self.model_results.fault_probs
                )
        
        return self.FAULT_ACTIVE, self.previous_phase

    def send_message(self, phase, predicted_fault_index, fault_probabilities):
        """
        Implements the Hysteresis Logic and Phase Transition Messaging.
        """
        FAULT_NAMES = ['No Clapping Detected', 'Clapping Motion'] 
        PHASE_NAMES = {0: "Setup", 1: "Eccentric", 2: "Concentric", 3: "Lockout", 4: "Stretch"}
        
        fault_name = FAULT_NAMES[predicted_fault_index]
        phase_name = PHASE_NAMES.get(phase, "Setup")
        fault_prob = fault_probabilities[predicted_fault_index]

        # --- Phase Transition Logic ---
        if self.previous_phase is not None and self.previous_phase != phase:
            print(f"🔄 PHASE TRANSITION: {PHASE_NAMES.get(self.previous_phase, 'Unknown')} -> {phase_name}")
        self.previous_phase = phase

        # 1. FAULT ACTIVATION LOGIC (T_Fault)
        if fault_name != 'No Clapping Detected' and fault_prob >= self.FAULT_THRESHOLD and not self.FAULT_ACTIVE:
            self.FAULT_ACTIVE = True
            print(f"🚨 CLAPPING DETECTED [{phase_name}]: {fault_name} ({fault_prob:.2f})")
            self.consecutive_good_frames = 0
            
        # 2. RECOVERY LOGIC (T_Recovery)
        elif self.FAULT_ACTIVE:
            # Check if 'No Clapping Detected' confidence meets the high recovery threshold
            good_form_prob = fault_probabilities[self.GOOD_FORM_INDEX]
            
            if good_form_prob >= self.RECOVERY_THRESHOLD:
                self.consecutive_good_frames += 1
                
                # Check for sustained recovery (5 consecutive frames)
                if self.consecutive_good_frames >= 5: 
                    self.FAULT_ACTIVE = False
                    print(f"✅ RECOVERY: Clapping Cleared! (Cleared in {phase_name})")
                    self.consecutive_good_frames = 0
            else:
                self.consecutive_good_frames = 0 
                
        # Update the display message based on the current state
        if self.FAULT_ACTIVE:
            self.current_message = f"CLAPPING: {fault_name}"
            self.text_color = (0, 0, 255) # Red/Blue for active detection
        else:
            self.current_message = f"Phase: {phase_name}"
            self.text_color = (0, 255, 0) # Green for good/base state


#Main thread:
main_queue = deque()

#Worker threads:
phase_change_queue = deque() #HMM
fault_detection_queue = deque() #Conv1D



"""
The section below defines the result callback.
Preferably you'd have the pose landmarks and barbell detected before the above functions are called:
"""


def result_format(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    logger.info("Pose landmarker result achieved, deadlift running ...")
    if result.pose_landmarks and session['bar_bbox']:
        #Eventually you need to handle the case of different equipment types too.
        exercise_alg = barbell.barbell_exercises[session['exercise']]
        #Only detect the straight barbells close to the camera, to enforce that only frames with barbell directly in front will be reviewed.
        message = exercise_alg(result.pose_landmarks[0], session['bar_bbox'], session['lift_stage'])

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

def powercoachalg(jpeg_data):
    numpy_frame = np.frombuffer(jpeg_data, np.uint8)
    logger.info("Converted jpeg data to numpy frame")
    
    cv_frame_rgb = cv.cvtColor(cv.imdecode(numpy_frame, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
    logger.info("Decompressed to RGB cv_frame")
    logger.info(f"Frame height: {cv_frame_rgb.shape[0]} pixels")
    logger.info(f"Frame width: {cv_frame_rgb.shape[1]} pixels")
    #^^^PRINT THE FRAME_HEIGHT AND FRAME_WIDTH AND MAKE SURE IT STAYED AT 256X256!

    mpframe = mp.Image(mp.ImageFormat.SRGB, data=cv_frame_rgb)
    logger.info("Converted to mediapipe frame")
        
    #Detecting poses from the image:
    frame_timestamp_ms = int((time.time() - session['start_time']) * 1000)
    
    bbell_detector_model.detect_async(mpframe, frame_timestamp_ms) #runs 10x a second
    logger.info("bbell detection model running ...")
    poselandmarker.detect_async(mpframe, frame_timestamp_ms)
    logger.info("pose landmarker model running ...")