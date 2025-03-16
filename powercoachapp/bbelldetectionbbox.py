import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector, ObjectDetectorOptions
import time

import os
assert os.path.exists('/Users/brian/Documents/Python/PowerCoach/models/bbelldetectionmodel.tflite'), "Model export failed!"

bbelldetection = ObjectDetector.create_from_model_path('/Users/brian/Documents/Python/PowerCoach/models/bbelldetectionmodel.tflite')

def bbellbbox(imagepath):
    image = mp.Image.create_from_file(imagepath)
    barbelldetections = bbelldetection.detect(image)

    barbell = ...
    for i in barbelldetections.detections:
        if (i.categories[0].category_name)=='Barbell':
            barbell = i
            break
            #This is because the highest confidence barbell will be at the top
                
    bbox = barbell.bounding_box
    
    return bbox

printresultbbox = None
#LIVE BARBELL DETECTION:
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global printresultbbox
    # Iterate through detections to find if any category is "barbell"
    for detection in result.detections:
        for category in detection.categories:
            if category.category_name == "Barbell" and category.score > 0.1:  #Gets first because its the highest confidence in the frame anyway
                print(f"Barbell detected with confidence: {category.score:.2f}")
                printresultbbox = detection.bounding_box
                print(f"Bounding box: {detection.bounding_box}")
                return
    
    printresultbbox = None
    print('No barbell found')
    return

livebbelldetectionoptions = ObjectDetectorOptions(
    base_options = mp.tasks.BaseOptions(model_asset_path = '/Users/brian/Documents/Python/PowerCoach/models/bbelldetectionmodel.tflite'),
    running_mode = mp.tasks.vision.RunningMode.LIVE_STREAM,
    result_callback = print_result
)

#if detections:
#    bbox = detections.detections[0].bounding_box #To be accessed in the powercoachalg
#    print(bbox)
#    cv2.rectangle(frame, (bbox.origin_x, bbox.origin_y), (bbox.origin_x+bbox.width, bbox.origin_y+bbox.height), (255,0,0), 2)

livebbelldetection = ObjectDetector.create_from_options(livebbelldetectionoptions)

def livebbellbbox():
    global printresultbbox
    
    cap = cv2.VideoCapture(0)  # 0 for default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    starttime = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
            break
        mpframe = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        timestamp_ms = int(1000*(time.time() - starttime))
        #CODE IT TO SHOW THE BOUNDING BOX!!!
        detections = livebbelldetection.detect_async(mpframe, timestamp_ms)

        print('START OF FRAME')
        if printresultbbox:
            print("Bounding box:", printresultbbox)
            cv2.rectangle(frame, (printresultbbox.origin_x, printresultbbox.origin_y), (printresultbbox.origin_x+printresultbbox.width, printresultbbox.origin_y+printresultbbox.height), (255,0,0), 2)
            
        cv2.imshow('Barbell detection', frame)  
        #MAKE SURE THIS IS A BARBELL:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return

#xlivebbellbbox()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def drawbbox(path, bbox):
    image = cv2.imread(path)
    cv2.rectangle(image, (bbox.origin_x, bbox.origin_y), (bbox.origin_x+bbox.width, bbox.origin_y+bbox.height), (255,0,0), 2)
    window_name = 'Image with bounding box'
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return
#[(bbox.origin_x, bbox.origin_y), (bbox.origin_x+bbox.width, bbox.origin_y+bbox.height)]