from sklearn.model_selection import train_test_split
import os, json
import cv2 as cv
import numpy as np

def cleaning_filenames():
    dir = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all'
    print(os.listdir(os.path.join(dir, 'images')))
    counter = 1
    if '.DS_Store' in os.listdir(os.path.join(dir, 'images')):
        os.remove(os.path.join(dir, 'images', '.DS_Store'))
    if '.DS_Store' in os.listdir(os.path.join(dir, 'labels')):
        os.remove(os.path.join(dir, 'labels', '.DS_Store'))
    
    for file_name in os.listdir(os.path.join(dir, 'images')):
        file_header = file_name[:-4]
        old_image_path = os.path.join(dir, 'images', file_header + '.jpg')
        new_image_path = os.path.join(dir, 'images', str(counter) + '.jpg')
        if os.path.exists(os.path.join(dir, 'labels', file_header + '.xml.txt')):
            old_label_path = os.path.join(dir, 'labels', file_header + '.xml.txt')
            new_label_path = os.path.join(dir, 'labels', str(counter) + '.txt')
        else:
            old_label_path = os.path.join(dir, 'labels', file_header + '.txt')
            new_label_path = os.path.join(dir, 'labels', str(counter) + '.txt')
        
        #Renaming file paths, but being safe so that files already renamed are not overwritten:
        if os.path.exists(new_image_path):
            print(f"WARNING: IMAGE PATH {new_image_path} already exists. Skipping.")
        else:
            os.rename(old_image_path, new_image_path)
        if os.path.exists(new_label_path):
            print(f"WARNING: LABEL PATH {new_label_path} already exists. Skipping.")
        else:  
            os.rename(old_label_path, new_label_path)
            
        #now do the same for the labels
        counter += 1
        
#cleaning_filenames()


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


#CREATING COCO DATASET WITH TRAIN/VAL/TEST SPLIT AND JSON FILES::
"""
def create_coco_dataset():
    #Splitting into train/val/test folders:
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
    
    #Removing .DS_Store:
    directories = os.listdir(testlabels)
    if '.DS_Store' in directories:
        directories.remove('.DS_Store')
        
    
    #Creating labels.json files:
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