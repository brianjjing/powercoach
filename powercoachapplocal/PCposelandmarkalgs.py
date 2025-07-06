import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

#Livestream drawing landmarks
def livestreamlandmarks():
    cap = cv2.VideoCapture(0)  # 0 for default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    with mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.8, min_tracking_confidence=0.8) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Exiting...")
                break

            # Convert the BGR frame to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame to detect pose
            results = pose.process(rgb_frame)

            # Draw the pose landmarks on the frame
            if results.pose_landmarks:
                #print(results.pose_landmarks)
                mp_drawing.draw_landmarks(
                    frame,  # Original BGR frame
                    results.pose_landmarks,  # Detected landmarks
                    mp_pose.POSE_CONNECTIONS  # Connections between landmarks
                )
            # Display the frame
            cv2.imshow('Pose Estimation', frame)

#['LEFT_ANKLE', 'LEFT_EAR', 'LEFT_ELBOW', 'LEFT_EYE', 'LEFT_EYE_INNER', 'LEFT_EYE_OUTER', 'LEFT_FOOT_INDEX', 'LEFT_HEEL', 'LEFT_HIP',
#'LEFT_INDEX', 'LEFT_KNEE', 'LEFT_PINKY', 'LEFT_SHOULDER', 'LEFT_THUMB', 'LEFT_WRIST', 'MOUTH_LEFT', 'MOUTH_RIGHT', 'NOSE', 
#'RIGHT_ANKLE', 'RIGHT_EAR', 'RIGHT_ELBOW', 'RIGHT_EYE', 'RIGHT_EYE_INNER', 'RIGHT_EYE_OUTER', 'RIGHT_FOOT_INDEX', 'RIGHT_HEEL', 
#'RIGHT_HIP', 'RIGHT_INDEX', 'RIGHT_KNEE', 'RIGHT_PINKY', 'RIGHT_SHOULDER', 'RIGHT_THUMB', 'RIGHT_WRIST']

            # Exit loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return

livestreamlandmarks()

def drawlandmarks(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pose = mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.8, min_tracking_confidence=0.8)
    results = pose.process(image)
    if results.pose_landmarks:
        #print(results.pose_landmarks)
        mp_drawing.draw_landmarks(
            image,  # Original BGR frame
            results.pose_landmarks,  # Detected landmarks
            mp_pose.POSE_CONNECTIONS  # Connections between landmarks
        )
        cv2.imshow('Pose Estimation', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return
    else:
        return "Error: No landmarks detected"
    
#drawlandmarks('/Users/brian/Downloads/DEADY8.jpeg')
