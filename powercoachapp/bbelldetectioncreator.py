import mediapipe as mp
from mediapipe_model_maker import object_detector
import os
import tensorflow as tf
import cv2 as cv
import numpy as np
from bs4 import BeautifulSoup
print("LIBRARIES LOADED IN")

#UNDERSTAND ALL THIS FOR NOW, OPTIMIZE LATER:
#RETRAINING PROCESS:
#FIND OUT HOW TO MAKE THE RETRAINING WORK, THEN MAKE A DATASET TO RETRAIN.
model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')
coco_path = os.path.join(os.path.dirname(__file__), 'bbelldetecset.coco')
cache_train = os.path.join(os.path.dirname(__file__), 'cachetrain')
cache_valid = os.path.join(os.path.dirname(__file__), 'cachevalid')
cache_test = os.path.join(os.path.dirname(__file__), 'cachetest')

dataset = coco_path
traindataset = os.path.join(dataset, 'train')
valdataset = os.path.join(dataset, 'val')
train_data = object_detector.Dataset.from_coco_folder(traindataset, cache_dir=cache_train)
validation_data = object_detector.Dataset.from_coco_folder(valdataset, cache_dir=cache_valid)

print("Creation starting:")
#TURN IMAGES INTO REQUIRED INPUT SIZE! (256X256)
spec = object_detector.SupportedModels.MOBILENET_V2
#Optimize parameters later:
exported_model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel')
hparams = object_detector.HParams(
    export_dir=exported_model_path
)
#REDUCE LR ON PLATEAU!!!
#Tweak regularization term?
options = object_detector.ObjectDetectorOptions(
    supported_model=spec,
    hparams=hparams
)

model = object_detector.ObjectDetector.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options)
print("CREATION DONE")

print("Exporting model:")
model.export_model(
    model_name = model_path
)
print("EXPORTING DONE")

#Do post-training quantization as well

testdataset = os.path.join(dataset, 'test')
test_data = object_detector.Dataset.from_coco_folder(testdataset, cache_dir=cache_test)

print("Evaluation:")
loss, coco_metrics = model.evaluate(test_data, batch_size=4)
print(f"Validation loss: {loss}")
print(f"Validation coco metrics: {coco_metrics}")
print("VALIDATION DONE")

#Problem: Low asf recall and precision, but mainly low asf recall. It can't detect a good QUANTITY of barbells, but of the barbells it detects, the QUALITY of detections was decent (decent amnt of things it detected were actually barbells)

"""BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
print(dir(ObjectDetector))
print('test')
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode


#Detect a barbell and get the coordinates of it!

#1. Retrain object_detector to recognize barbells from the front view
    #Webscrape a dataset for barbells from the web (know how to pick good data) - MANUALLY LABEL THEM W LABELIMG (start w 100 images)
        #Make them into a COCO file
    #Retrain the model and just get accuracy at first
    #Then go into optimizing the parametersf
#2. Use the barbell locations in your hueristic functions"""

"""import cv2 as cv
[0,290,332,36]
image = cv.imread('/Users/brian/Downloads/Barbell detection 2.v1i.coco/train/barbellvideo2-9de8a21c-2c08-11ee-9f6f-d41b816bdd7c_jpg.rf.e34a44cdd1e3378b5f72d57b60eb412a.jpg')
bboximage = cv.rectangle(image.copy(), (0,400), (332,400+36), (255,0,0))


cv.imshow('Bounding Box', bboximage)
cv.waitKey(0)
cv.destroyAllWindows"""


#LIVE STREAM TO USE THE BARBELL OBJECT DETECTOR MODEL IN LATER:
"""
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    # Iterate through detections to find if any category is "barbell"
    for detection in result.detections:
        for category in detection.categories:
            if category.category_name == "person" and category.score > 0.5:  # Example threshold
                print(f"Person detected with confidence: {category.score:.2f}")
                print(f"Bounding box: {detection.bounding_box}")
                return
    print('No person found')
    return

options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path='/Users/brian/Documents/Python/PowerCoach/models/objectdetection_efficientdet_lite0.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    max_results=3,
    result_callback=print_result)

import cv2 as cv
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

import time

with ObjectDetector.create_from_options(options) as detector:
    starttime = time.time()
    while True:
    # The detector is initialized. Use it here.
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
            break
        framergb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mpimage = mp.Image(image_format = mp.ImageFormat.SRGB, data=framergb)
        frame_timestamp_ms = int((time.time() - starttime) * 1000)
        detection_result = detector.detect_async(mpimage, frame_timestamp_ms)
        
        #See if detected object is a barbell
        
        cv.imshow('Pose Estimation', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv.destroyAllWindows()
"""

#Web scraping images:
"""import requests
from bs4 import BeautifulSoup
import csv
print("SUCCESS LOADING IN SCRAPING LIBRARIES")

url = #URL you want to scrape
header = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=header)
soup = BeautifulSoup(r.text, 'html.parser')
images = soup.find_all('a', attrs={'class':'sdms-image-result'})
print(len(images))

for i in np.arange(len(images)):
    open(f'deadlift{i}.jpg', 'wb').write(requests.get(images[i].img['data-src']).content)
print('SUCCESSFULLY WROTE IMAGES')"""

#Seeing how bad the current dataset is:
"""
labels_json = json.load(open('/Users/brian/Documents/Python/PowerCoach/bbdetection2.v1i.coco/train/labels.json', "r"))
trainimages = labels_json['images']
trainannotations = labels_json['annotations']
for i in np.arange(38):
    image = cv.imread(os.path.join('/Users/brian/Documents/Python/PowerCoach/bbdetection2.v1i.coco/train/images', trainimages[i]['file_name']))
    imagewbox = cv.rectangle(image, (int(trainannotations[i]['bbox'][0]),int(trainannotations[i]['bbox'][1])), (int(trainannotations[i]['bbox'][0]+trainannotations[i]['bbox'][2]),int(trainannotations[i]['bbox'][1]+trainannotations[i]['bbox'][3])), (255,0,0), 2)
    cv.imwrite(f'ogboundingboximage{i}.jpg', imagewbox)
"""

#Moving files around and making files:
"""
os.makedirs(traindir, exist_ok=True)
os.makedirs(valdir, exist_ok=True)
os.makedirs(testdir, exist_ok=True)
try:
    images = [file for file in os.listdir(imagefolder) if os.path.isfile(os.path.join(imagefolder, file))]

    train, valtest = train_test_split(images, test_size=0.3, random_state=420)
    val, test = train_test_split(valtest, test_size=0.5, random_state=420)

    for i in train:
        os.rename(os.path.join(imagefolder, i), os.path.join(traindir, i))
    for i in val:
        os.rename(os.path.join(imagefolder, i), os.path.join(valdir, i))
    for i in test:
        os.rename(os.path.join(imagefolder, i), os.path.join(testdir, i))
except:
    print('Not enough images in imagefolder, images already split')
"""

#CREATING DATASET:
#COCO DATASET:
"""
from sklearn.model_selection import train_test_split

#Directories:
imagefolder = '/Users/brian/Documents/Python/PowerCoach/bbelldetecset.coco'
traindir = os.path.join(imagefolder, 'train')
trainimages = os.path.join(traindir, 'images')
trainlabels = os.path.join(traindir, 'labels')

valdir = os.path.join(imagefolder, 'val')
valimages = os.path.join(valdir, 'images')
vallabels = os.path.join(valdir, 'labels')

testdir = os.path.join(imagefolder, 'test')
testimages = os.path.join(testdir, 'images')
testlabels = os.path.join(testdir, 'labels')

#Initializing coco dataset lists (Categories list already made):
barbellid = 1
cocodataset = {
    'categories':[
        {"id":barbellid, "name":"Barbell"}
    ],
    'images':[],
    'annotations':[]
}
cocoimages = []
cocoannotations = []
id = 0

#Removing .DS_Store
directories = os.listdir(testlabels)
if '.DS_Store' in directories:
    directories.remove('.DS_Store')
    
for i in directories:
    #Making images list:
    if i.endswith('.xml.txt'):
        imagefile = i.replace('.xml.txt','.jpg')
    else:
        imagefile = i.replace('.txt','.jpg')
    imagedic = {}
    imagedic['id'] = id
    imagedic['file_name'] = imagefile
    image = cv.imread(os.path.join(testimages, imagefile))
    imageheight, imagewidth, channels = image.shape
    imagedic['height'] = imageheight
    imagedic['width'] = imagewidth
    cocoimages.append(imagedic)
    
    #Annotations list:
    #Add segmentation to the annotations?
    annotationsdic = {}
    annotationsdic['id'] = id
    annotationsdic['image_id'] = id
    annotationsdic['category_id'] = barbellid
    
    yoloannotations = (open(os.path.join(testlabels, i), 'r').read()).split(' ')
    bboxheight = int(imageheight * float(yoloannotations[-1].strip()))
    bboxcenterx = int(imagewidth * float(yoloannotations[1]))
    bboxcentery = int(imageheight * float(yoloannotations[2]))
    bboxwidth = int(imagewidth * float(yoloannotations[3]))
    bbox = [(bboxcenterx - (bboxwidth)/2), (bboxcentery - (bboxheight)/2), bboxwidth, bboxheight]
    annotationsdic['bbox'] = bbox
    annotationsdic['area'] = bboxheight*bboxwidth
    cocoannotations.append(annotationsdic)

    id += 1

cocodataset['images'] = cocoimages
cocodataset['annotations'] = cocoannotations

with open(os.path.join(testdir, 'labels.json'), 'w') as cocodatasetjson:
    json.dump(cocodataset, cocodatasetjson, indent=4)
print("SUCCESS CREATING DATASET")"""