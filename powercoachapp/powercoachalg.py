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
import joblib

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
    """
    Extracts kinematic features from pose landmarks and barbell bounding box.
    Returns a feature vector of length N_FEATURES (10 features).
    
    Features for barbell exercises:
    0-1: Left and right hip-knee angles (leg extension)
    2-3: Left and right shoulder-hip-knee angles (back angle)
    4-5: Left and right knee angles (ankle-knee-hip)
    6-7: Left and right elbow angles (arm position)
    8: Barbell Y position (normalized to frame height)
    9: Barbell X position (normalized to frame width)
    """
    n_features = sliding_window_framework_metadata['N_FEATURES']
    feature_vector = np.zeros(n_features, dtype=np.float32)
    
    # Handle missing pose landmarks
    if pose_landmarks is None:
        return feature_vector
    
    mp_pose = mp.solutions.pose
    mplandmarks = mp.solutions.pose.PoseLandmark
    
    # Handle different pose_landmarks structures:
    # - If it's a list of poses (from PoseLandmarkerResult), take the first one
    # - If it's already a landmark list, use it directly
    landmarks = None
    if isinstance(pose_landmarks, list) and len(pose_landmarks) > 0:
        # Check if first element is a landmark list or if the list itself contains landmarks
        if hasattr(pose_landmarks[0], '__getitem__') or hasattr(pose_landmarks[0], '__len__'):
            # Try to access as if first element is a landmark list
            try:
                _ = pose_landmarks[0][mplandmarks.LEFT_HIP]
                landmarks = pose_landmarks[0]
            except (IndexError, KeyError, TypeError):
                # If that fails, try using the list directly
                landmarks = pose_landmarks
        else:
            landmarks = pose_landmarks
    else:
        landmarks = pose_landmarks
    
    # Get key landmarks
    try:
        left_hip = landmarks[mplandmarks.LEFT_HIP]
        right_hip = landmarks[mplandmarks.RIGHT_HIP]
        left_knee = landmarks[mplandmarks.LEFT_KNEE]
        right_knee = landmarks[mplandmarks.RIGHT_KNEE]
        left_ankle = landmarks[mplandmarks.LEFT_ANKLE]
        right_ankle = landmarks[mplandmarks.RIGHT_ANKLE]
        left_shoulder = landmarks[mplandmarks.LEFT_SHOULDER]
        right_shoulder = landmarks[mplandmarks.RIGHT_SHOULDER]
        left_elbow = landmarks[mplandmarks.LEFT_ELBOW]
        right_elbow = landmarks[mplandmarks.RIGHT_ELBOW]
        left_wrist = landmarks[mplandmarks.LEFT_WRIST]
        right_wrist = landmarks[mplandmarks.RIGHT_WRIST]
    except (IndexError, KeyError, AttributeError, TypeError):
        # If any landmark is missing, return zero vector
        return feature_vector
    
    # Feature 0-1: Hip-Knee-Ankle angles (leg extension)
    # Left leg
    feature_vector[0] = barbell.calculate_angle(left_hip, left_knee, left_ankle)
    # Right leg
    feature_vector[1] = barbell.calculate_angle(right_hip, right_knee, right_ankle)
    
    # Feature 2-3: Shoulder-Hip-Knee angles (back angle/posture)
    # Left side
    feature_vector[2] = barbell.calculate_angle(left_shoulder, left_hip, left_knee)
    # Right side
    feature_vector[3] = barbell.calculate_angle(right_shoulder, right_hip, right_knee)
    
    # Feature 4-5: Knee angles (Ankle-Knee-Hip, alternative leg angle)
    # Left leg
    feature_vector[4] = barbell.calculate_angle(left_ankle, left_knee, left_hip)
    # Right leg
    feature_vector[5] = barbell.calculate_angle(right_ankle, right_knee, right_hip)
    
    # Feature 6-7: Elbow angles (Shoulder-Elbow-Wrist, arm position)
    # Left arm
    feature_vector[6] = barbell.calculate_angle(left_shoulder, left_elbow, left_wrist)
    # Right arm
    feature_vector[7] = barbell.calculate_angle(right_shoulder, right_elbow, right_wrist)
    
    # Feature 8-9: Barbell position (normalized coordinates)
    if bbell_bbox is not None:
        # Normalize barbell center Y position (0.0 = top, 1.0 = bottom)
        bbell_center_y = (bbell_bbox.origin_y + bbell_bbox.height / 2) / frame_height
        feature_vector[8] = np.clip(bbell_center_y, 0.0, 1.0)
        
        # Normalize barbell center X position (0.0 = left, 1.0 = right)
        bbell_center_x = (bbell_bbox.origin_x + bbell_bbox.width / 2) / frame_width
        feature_vector[9] = np.clip(bbell_center_x, 0.0, 1.0)
    else:
        # If no barbell detected, set to default values (middle-bottom of frame)
        feature_vector[8] = 0.8  # Default to lower portion
        feature_vector[9] = 0.5  # Default to center
    
    return feature_vector

def run_fault_thread(*args):
    #Conv1D - Perform the inference!
    return

def load_or_create_hmm(n_states, n_features):
    """
    Loads a pre-trained HMM model from file or creates a mock one for testing.
    In production, this should load from a deployed model path.
    
    Args:
        n_states: Number of HMM states (phases)
        n_features: Number of features per frame
        
    Returns:
        Trained HMM model (hmmlearn.GaussianHMM)
    """
    hmm_model_path = os.path.join(os.path.dirname(__file__), 'models', 'deadlift_phase_hmm.pkl')
    
    try:
        if os.path.exists(hmm_model_path):
            loaded_hmm = joblib.load(hmm_model_path)
            logger.info(f"Loaded pre-trained HMM model from {hmm_model_path}")
            return loaded_hmm
    except Exception as e:
        logger.warning(f"Could not load HMM model: {e}. Creating mock model.")
    
    # Create a mock HMM model for testing/development
    logger.info("Creating mock GaussianHMM for development...")
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=10
    )
    # Train on mock data to initialize the model
    X_mock = np.random.rand(4 * 5, n_features)  # 4 frames * 5 sequences
    lengths = [4] * 5
    model.fit(X_mock, lengths)
    
    # Save the mock model for future use
    try:
        os.makedirs(os.path.dirname(hmm_model_path), exist_ok=True)
        joblib.dump(model, hmm_model_path)
        logger.info(f"Saved mock HMM model to {hmm_model_path}")
    except Exception as e:
        logger.warning(f"Could not save mock HMM model: {e}")
    
    return model

def run_phase_thread(hmm_model, window_data, results_obj):
    """
    Target function for HMM thread: runs decode to determine phase sequence.
    Sets the phase result in the shared results object.
    
    Args:
        hmm_model: Trained HMM model (hmmlearn.GaussianHMM)
        window_data: 2D numpy array of shape (window_size, n_features)
        results_obj: SlidingWindowResults object to store the phase result
    """
    try:
        if hmm_model is None or window_data is None or len(window_data) == 0:
            logger.warning("HMM thread: Invalid model or data")
            return
        
        # HMM decode returns (log_probability, state_sequence)
        # state_sequence is an array of predicted states for each frame in the window
        log_prob, phase_sequence = hmm_model.decode(window_data)
        
        # Get the phase for the most recent frame (last element in sequence)
        if len(phase_sequence) > 0:
            results_obj.phase = int(phase_sequence[-1])
            logger.debug(f"HMM thread: Phase detected = {results_obj.phase}, log_prob = {log_prob:.2f}")
        else:
            logger.warning("HMM thread: Empty phase sequence")
            
    except Exception as e:
        logger.error(f"HMM thread error: {str(e)}", exc_info=True)
        # On error, don't update phase (keep previous value)

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
        self.hmm_model = load_or_create_hmm(n_hmm_states, n_features)
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
            if (len(self.sliding_window) == self.window_size) and (self.frames_since_last_process >= HOP_SIZE):
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