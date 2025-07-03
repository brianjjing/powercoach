import time
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector, ObjectDetectorOptions
from powercoachapp.extensions import logger
from powercoachapp.bbelldetectioncreator import bbell_detector_model, barbell_bounding_box

import os
model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')
assert os.path.exists(model_path), "Model not exported! Please run bbelldetectioncreator.py to export the model."


#DRAWING bounding box live:
def livebbellbbox():
    global printresultbbox
    
    cap = cv.VideoCapture(0)  # 0 for default webcam
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
        bbell_detector_model.detect_async(mpframe, timestamp_ms)

        print('START OF FRAME')
        if printresultbbox:
            print("Bounding box:", printresultbbox)
            cv.rectangle(frame, (printresultbbox.origin_x, printresultbbox.origin_y), (printresultbbox.origin_x+printresultbbox.width, printresultbbox.origin_y+printresultbbox.height), (255,0,0), 2)
            
        cv.imshow('Barbell detection', frame)  
        #MAKE SURE THIS IS A BARBELL:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    return

#livebbellbbox()

#GETTING bounding box based on still image
def bbellbbox(imagepath):
    image = mp.Image.create_from_file(imagepath)
    barbelldetections = bbell_detector_model.detect_async(image, 1000)

    barbell = None
    for i in barbelldetections.detections:
        if (i.categories[0].category_name)=='Barbell':
            barbell = i
            break
            #This is because the highest confidence barbell will be at the top
                
    bbox = barbell.bounding_box

    return bbox

#DRAWING bounding box on still image
def drawbbox(path, bbox):
    image = cv.imread(path)
    cv.rectangle(image, (bbox.origin_x, bbox.origin_y), (bbox.origin_x+bbox.width, bbox.origin_y+bbox.height), (255,0,0), 2)
    window_name = 'Image with bounding box'
    cv.imshow(window_name, image)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return
#[(bbox.origin_x, bbox.origin_y), (bbox.origin_x+bbox.width, bbox.origin_y+bbox.height)]

drawbbox('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all/images/123.jpg', bbellbbox('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all/images/250.jpg'))