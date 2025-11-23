"""
Proof of concept for the new form correction framework:
- Using a sliding window approach (will optimize frame count and hop size later)
- Splitting each window analysis into two parallel threads:
    1. Hidden Markov Model for Phase Detection (is the movement on concentric or eccentric?)
    2. Conv1D for Fault Detection (detecting fault anomalies)
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, GlobalAveragePooling1D, Dense
from hmmlearn import hmm # HMM Library
import joblib
import os
import warnings
import threading # CRITICAL: Import threading for parallel execution
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
WINDOW_LEN = 4          # SEQUENCE LENGTH: Set to 4 frames for low latency testing
N_MOTION_CLASSES = 2
N_FEATURES = 10         # Total number of kinematic features (Input size for both models)
N_HMM_STATES = 4        # 0: Setup, 1: Eccentric, 2: Concentric, 3: Lockout
N_FAULT_CLASSES = 2     # 0: No Clapping, 1: Clapping Motion
MODEL_WEICHTS_PATH = 'clapping_cnn_weights.h5'
HOP_SIZE = 1            # CRITICAL: Set hop to 1 to run inference on every new frame
DEVICE = 'CPU'          
CONFIDENCE_THRESHOLD = 0.8

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# --- GLOBAL WRAPPER CLASS FOR THREAD RESULTS ---
#Holding the PHASE and FAULT PROBS.
class ModelResults:
    """Safely holds the results from concurrent model threads."""
    def __init__(self):
        self.phase = None
        self.fault_probs = None

# --- THREAD TARGET FUNCTIONS ---

#Input the model, window data, and results objected.
def run_hmm_threaded(hmm_model, window_data, results_obj):
    """Target function for HMM thread: runs decode and saves phase result."""
    log_prob, phase_sequence = hmm_model.decode(window_data)
    results_obj.phase = phase_sequence[-1] # Get the phase for the newest frame

def run_cnn_threaded(cnn_model, sequence_tensor, results_obj):
    """Target function for CNN thread: runs prediction and saves fault probabilities."""
    predictions = cnn_model.predict(sequence_tensor, verbose=0)
    results_obj.fault_probs = predictions[0]

# --- 1. CONV1D MODEL ARCHITECTURE (FIXED) ---

def build_motion_cnn(window_len, n_features, n_classes):
    """Defines a simple 1D CNN optimized for speed."""
    model = Sequential([
        # FIX: Added padding='same' to ensure sequence length (time dimension) remains consistent
        Conv1D(filters=16, kernel_size=3, padding='same', activation='relu', input_shape=(window_len, n_features)),
        Conv1D(filters=32, kernel_size=3, padding='same', activation='relu'),
        GlobalAveragePooling1D(), 
        Dense(16, activation='relu'),
        Dense(n_classes, activation='softmax')
    ])
    
    # --- MOCK WEIGHTS LOADING (CRITICAL FOR INITIAL RUN) ---
    try:
        model.load_weights(MODEL_WEICHTS_PATH)
        print("Loaded pre-trained CNN weights.")
    except Exception:
        print("Creating mock CNN weights.")
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        # Use WINDOW_LEN=4 here for mock training data size
        model.fit(np.random.rand(1, window_len, n_features), np.array([0]), epochs=1, verbose=0)
        model.save_weights(MODEL_WEICHTS_PATH)
        
    return model

# --- 2. HMM MODEL FOR PHASE DETECTION ---

def load_or_train_hmm(X_train_sequences, n_states, n_features):
    """Loads a pre-trained HMM model or trains a mock one on random data."""
    HMM_MODEL_PATH = "deadlift_phase_hmm.pkl"
    try:
        loaded_hmm = joblib.load(HMM_MODEL_PATH)
        print("Loaded pre-trained HMM model.")
        return loaded_hmm
    except FileNotFoundError:
        print("Training mock GaussianHMM...")
        model = hmm.GaussianHMM(
            n_components=n_states, 
            covariance_type="full", 
            n_iter=10
        )
        # Create mock input data 
        X_mock = np.random.rand(4 * 5, n_features) # Using 4 frames * 5 sequences for mock data
        lengths = [4] * 5
        model.fit(X_mock, lengths)
        joblib.dump(model, HMM_MODEL_PATH)
        return model

# --- 3. FEATURE EXTRACTION ---

def extract_clapping_features(results, frame_height, frame_width):
    # ... (Feature extraction logic remains the same) ...
    if not results.pose_landmarks:
        return np.zeros(N_FEATURES, dtype=np.float32)

    landmarks = results.pose_landmarks.landmark
    feature_vector = np.zeros(N_FEATURES, dtype=np.float32)
    
    # Feature 0-7: Wrist and Elbow X, Y coordinates
    feature_vector[0] = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x
    feature_vector[1] = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
    feature_vector[2] = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x
    feature_vector[3] = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y
    feature_vector[4] = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x
    feature_vector[5] = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y
    feature_vector[6] = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x
    feature_vector[7] = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y
    
    # Features 8-9 (Difference features)
    feature_vector[8] = abs(feature_vector[0] - feature_vector[2]) # Distance between wrists (X)
    feature_vector[9] = abs(feature_vector[1] - feature_vector[3]) # Distance between wrists (Y)
    
    return feature_vector

# --- 4. THE REAL-TIME SLIDING WINDOW PIPELINE CLASS ---

class RealTimeFormCorrector:
    def __init__(self, window_size, n_features, n_hmm_states, n_fault_classes):
        
        self.window_size = window_size
        self.n_features = n_features
        self.buffer = deque(maxlen=window_size) 
        
        self.previous_phase = None
        self.frame_counter = 0 
        
        # Initialize models
        self.hmm_model = load_or_train_hmm([np.random.rand(window_size, n_features)], n_hmm_states, n_features) 
        self.cnn_fault_model = build_motion_cnn(window_size, n_features, n_fault_classes)
        # Initialize Keras predictor
        self.cnn_fault_model.predict(np.random.rand(1, window_size, n_features), verbose=0) 
        
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

# --- MAIN LIVESTREAM FUNCTION ---

def livestreamlandmarks():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    # --- INITIALIZE CORRECTOR AND MODELS ---
    # N_MOTION_CLASSES is used for N_FAULT_CLASSES in this demo setup
    corrector = RealTimeFormCorrector(WINDOW_LEN, N_FEATURES, N_HMM_STATES, N_MOTION_CLASSES)
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_height, frame_width, _ = frame.shape
            
            # 1. MediaPipe Processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False 
            results = pose.process(rgb_frame)
            rgb_frame.flags.writeable = True
            
            # 2. Process frame through the sequential pipeline
            corrector.process_frame(results, frame_height, frame_width, HOP_SIZE)
            
            # 3. Drawing and Display
            
            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Display the real-time classification message
            cv2.putText(frame, corrector.current_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, corrector.text_color, 2)
            
            # Display the frame
            cv2.imshow('Pose Estimation & Analysis', frame)

            # Exit loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    
# Execute the live streaming function
if __name__ == '__main__':
    livestreamlandmarks()