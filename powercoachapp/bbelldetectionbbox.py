import time
import cv2 as cv
import mediapipe as mp
from flask import session
from powercoachapp.bbelldetectioncreatemodel import bbell_detector_model

import os
model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')
assert os.path.exists(model_path), "Model not exported! Please run bbelldetectioncreator.py to export the model."

#DRAWING bounding box live:
"""
def livebbellbbox():    
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
        if barbell_bounding_box:
            print("Bounding box:", barbell_bounding_box)
            cv.rectangle(frame, (barbell_bounding_box.origin_x, barbell_bounding_box.origin_y), (barbell_bounding_box.origin_x+barbell_bounding_box.width, barbell_bounding_box.origin_y+barbell_bounding_box.height), (255,0,0), 2)
            
        cv.imshow('Barbell detection', frame)  
        #MAKE SURE THIS IS A BARBELL:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    return
#livebbellbbox()
"""

#GETTING bounding box based on still image
def bbellbbox(imagepath):
    image = mp.Image.create_from_file(imagepath)
    barbelldetections = bbell_detector_model.detect_async(image, 1000)

    barbell = None
    if barbelldetections.detections:
        for i in barbelldetections.detections:
            if (i.categories[0].category_name)=='Barbell':
                barbell = i
                bbox = barbell.bounding_box
                return bbox
                #This is because the highest confidence barbell will be at the top
    else:
        return "No barbell detected"
    

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
#drawbbox('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/test/images/352.jpg', bbellbbox('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/test/images/352.jpg'))


#Draw a rotated rectangle with minAreaRect.
def testing_yolo_labels(image_num):
    #.txt label files are in YOLO format, COCO format files are only in the .json file
    image = cv.imread(f'/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/doneimages/{image_num}.jpg')
    height, width, _ = image.shape
    with open(f'/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/donelabels/{image_num}.txt', 'r') as f:
        bbox_data = f.read().strip().split(' ')
        bboxcenterx = int(width * float(bbox_data[1]))
        bboxcentery = int(height * float(bbox_data[2]))
        bboxwidth = int(width * float(bbox_data[3]))
        bboxheight = int(height * float(bbox_data[4]))
        cv.rectangle(image, (bboxcenterx-bboxwidth//2, bboxcentery-bboxheight//2), (bboxcenterx+bboxwidth//2, bboxcentery+bboxheight//2), (255,0,0))
        window_name = 'Image with bounding box'
        cv.imshow(window_name, image)
        cv.waitKey(0)
        cv.destroyAllWindows()
        
#testing_yolo_labels(120)

#Put this in the bbox file:
def detect_in_image(path):
    start_time = time.time()
    image = mp.Image.create_from_file(path)

    print("IMAGE: ", image)
    bbell_detector_model.detect_async(image, timestamp_ms=int((time.time() - start_time) * 1000))
    time.sleep(1)

    image_np = image.numpy_view()
    image_bgr = cv.cvtColor(image_np, cv.COLOR_RGB2BGR)
    cv.rectangle(image_bgr, (session['bar_bbox'].origin_x, session['bar_bbox'].origin_y), (session['bar_bbox'].origin_x+session['bar_bbox'].width, session['bar_bbox'].origin_y+session['bar_bbox'].height), (255,0,0), 2)
    cv.imshow("Detected Image", image_bgr)
    cv.waitKey(0)
    cv.destroyAllWindows()
#detect_in_image('/Users/brian/Downloads/man-working-out-in-a-gym-with-barbell-and-weights-royalty-free-image-1694172345.avif')