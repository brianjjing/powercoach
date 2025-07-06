from sklearn.model_selection import train_test_split
import os, json, requests, csv, time
import cv2 as cv
import numpy as np
from bs4 import BeautifulSoup
from powercoachapp.bbelldetectiondatasetapikeys import GOOGLE_SEARCH_API_KEY

def cleaning_filenames():
    dir = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/allnotdone'
    print(os.listdir(os.path.join(dir, 'images')))
    counter = 252
    if '.DS_Store' in os.listdir(os.path.join(dir, 'images')):
        os.remove(os.path.join(dir, 'images', '.DS_Store'))
    if '.DS_Store' in os.listdir(os.path.join(dir, 'labels')):
        os.remove(os.path.join(dir, 'labels', '.DS_Store'))
    
    for file_name in os.listdir(os.path.join(dir, 'images')):
        file_header = file_name[:-4]
        old_image_path = os.path.join(dir, 'images', file_header + '.jpg')
        new_image_path = os.path.join(dir, 'images', str(counter) + '.jpg')
        if os.path.exists(os.path.join(dir, 'labels', file_header + '.txt')):
            old_label_path = os.path.join(dir, 'labels', file_header + '.txt')
            new_label_path = os.path.join(dir, 'labels', str(counter) + '.txt')
        else:
            continue  # Skip if label file does not exist
        
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

#Web scraping images for dataset:
#TOTAL WORKFLOW:
#1. Web scrape images

#2. Use LabelImg to label them (CURRENTLY ON)
    #NOW GO THROUGH ALL THE IMAGES, AND IF IT DOESN'T HAVE A CORRESPONDING LABEL FILE, THEN DELETE IT:

#3. Convert to coco dataset w/ annotations

#4. Make train/test/val splits, and retrain model. See new accuracy.


#Google Search API Code:
def google_search_api_web_scraping():
    API_KEY = GOOGLE_SEARCH_API_KEY

    dir = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all'
    #Now change the following code to get barbell images:

    query_list = [
        #All your queries
    ]
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        #'q': "deadlift barbell tiktok vertical photo",                # Search query
        'key': API_KEY,            # API Key
        'cx': "50ffc3b66006242a2",                  # Custom Search Engine ID
        'searchType': 'image',  # Filter for realistic, camera-taken photos
        'imgType': 'photo', # Specify we want image results
        'num': 10,   # Return only the first image result
    }
    already_iterated = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    for query in query_list:
        for start_index in range(1, 51, 10):  # Adjust the range as needed
            try:
                params['start'] = start_index
                params['q'] = query
                response = requests.get(url, headers=headers, params=params, timeout=5)
                results = response.json()
                
                time.sleep(1)  # To avoid hitting the API too fast

                portrait_count = 0
                landscape_count = 0
                square_count = 0
                if results['items']:
                    for item in results['items']:
                        if item['link']:
                            if item['link'] in already_iterated:
                                print(f"Skipping already iterated link: {item['link']}")
                                continue
                            print(item['link'])
                            already_iterated.add(item['link'])
                            if item['image']['height'] > item['image']['width']:
                                portrait_count += 1
                            if item['image']['width'] > item['image']['height']:
                                landscape_count += 1
                            else:
                                square_count += 1
                                
                            response = requests.get(item['link'], headers=headers, timeout=5)
                            time.sleep(1)  # To avoid hitting the API too fast
                            
                            if response.status_code == 200:
                                with open(os.path.join(dir, 'images', f"!!{item['link'].split('/')[-1]}.jpg"), 'wb') as f:
                                    f.write(response.content)
                                print("Image successfully downloaded")
                            else:
                                print(f"Failed to download image, status code: {response.status_code}")

                        print(portrait_count)
                        print(landscape_count)
                        print(square_count)
                        print("--------------------------------------------------")
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(5)
                
#google_search_api_web_scraping()

#Next steps for better dataset, get from different browsers: TikTok and Bing


#Beautiful Soup Web Scraping Code, but you should just use the Google Search API instead:
def beautiful_soup_web_scraping():
    url = "" #URL you want to scrape
    header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')
    images = soup.find_all('a', attrs={'class':'sdms-image-result'})
    print(len(images))

    for i in np.arange(len(images)):
        open(f'deadlift{i}.jpg', 'wb').write(requests.get(images[i].img['data-src']).content)
    print('SUCCESSFULLY WROTE IMAGES')

#beautiful_soup_web_scraping()


def deleting_unannotated_images():
    dir = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/allnotdone'
    images = os.listdir(os.path.join(dir, 'images'))[0:-4]
    images = [image[0:-4] for image in images] #Remove the .jpg extension from the image names
    labels = os.listdir(os.path.join(dir, 'labels'))[0:-4]
    labels = [label[0:-4] for label in labels] #Remove the .txt extension from the label names
    
    for image in images:
        if image not in labels:
            print(f"Deleting {image} as it has no label file")
            os.remove(os.path.join(dir, 'images', f'{image}.jpg'))
            
    print("Done deleting unannotated images")

#deleting_unannotated_images()


#CREATING COCO DATASET WITH TRAIN/VAL/TEST SPLIT AND JSON FILES:

#Current problem:
# (py3.11venv) brian@Mac PowerCoach % python3 -m powercoachapp.bbelldetectiondatasetcreator
# [ WARN:0@0.162] global loadsave.cpp:241 findDecoder imread_('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/train/labels/63.jpg'): can't open/read file: check file path/integrity
# Traceback (most recent call last):
#   File "<frozen runpy>", line 198, in _run_module_as_main
#   File "<frozen runpy>", line 88, in _run_code
#   File "/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetectiondatasetcreator.py", line 262, in <module>
#     create_coco_dataset()
#   File "/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetectiondatasetcreator.py", line 231, in create_coco_dataset
#     imageheight, imagewidth, channels = image.shape

def create_coco_dataset():
    #Splitting into train/val/test folders:
    basefolder = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone'
    imagefolder = os.path.join(basefolder, 'doneimages')
    traindir = os.path.join(basefolder, 'train')
    trainimages = os.path.join(traindir, 'images')
    trainlabels = os.path.join(traindir, 'labels')

    valdir = os.path.join(basefolder, 'val')
    valimages = os.path.join(valdir, 'images')
    vallabels = os.path.join(valdir, 'labels')

    testdir = os.path.join(basefolder, 'test')
    testimages = os.path.join(testdir, 'images')
    testlabels = os.path.join(testdir, 'labels')

    os.makedirs(traindir, exist_ok=True)
    os.makedirs(valdir, exist_ok=True)
    os.makedirs(testdir, exist_ok=True)
    try:
        images = [file for file in os.listdir(imagefolder) if os.path.isfile(os.path.join(imagefolder, file))]

        train, valtest = train_test_split(images, test_size=0.2, random_state=420)
        val, test = train_test_split(valtest, test_size=0.5, random_state=420)

        #Moving the images w/ renaming:
        for i in train:
            os.rename(os.path.join(imagefolder, i), os.path.join(trainimages, i))
        for i in val:
            os.rename(os.path.join(imagefolder, i), os.path.join(valimages, i))
        for i in test:
            os.rename(os.path.join(imagefolder, i), os.path.join(testimages, i))
    except:
        print('Not enough images in imagefolder, images already split')
    
    #Turning the split image folders into label folders:
    splitimagefolders = [trainimages, valimages, testimages]
    labeldirorders = [trainlabels, vallabels, testlabels]
    for i in range(3):
        #Removing .DS_Store:
        splitimagefolderdir = os.listdir(splitimagefolders[i]) #Doesn't do whole dir before file name, just the name of the file w reference to the directory
        labelfolderdir = [os.path.join(labeldirorders[i], file.replace('jpg', 'txt')) for file in splitimagefolderdir] #Gets all the label files in the split
        if '.DS_Store' in labelfolderdir:
            labelfolderdir.remove('.DS_Store')
            
        
        #Creating labels.json file:
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
            
        for label in labelfolderdir:
            #Making images list:
            imagefile = label.replace('.txt','.jpg')
            imagedic = {}
            imagedic['id'] = id
            imagedic['file_name'] = imagefile
            image = cv.imread(os.path.join(splitimagefolders[i], imagefile))
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
            
            yoloannotations = (open(os.path.join(labeldirorders[i], label), 'r').read()).split(' ')
            bboxcenterx = int(imagewidth * float(yoloannotations[1]))
            bboxcentery = int(imageheight * float(yoloannotations[2]))
            bboxwidth = int(imagewidth * float(yoloannotations[3]))
            bboxheight = int(imageheight * float(yoloannotations[-1].strip()))
            bbox = [(bboxcenterx - (bboxwidth)/2), (bboxcentery - (bboxheight)/2), bboxwidth, bboxheight]
            annotationsdic['bbox'] = bbox
            annotationsdic['area'] = bboxheight*bboxwidth
            cocoannotations.append(annotationsdic)

            id += 1

        cocodataset['images'] = cocoimages
        cocodataset['annotations'] = cocoannotations

        with open(os.path.join(labeldirorders[i], 'labels.json'), 'w') as cocodatasetjson:
            json.dump(cocodataset, cocodatasetjson, indent=4)
        print(f"SUCCESS CREATING DATASET")

#create_coco_dataset()

def redirect_to_main_image_folder():
    main_image_folder = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/doneimages'
    
    for path in os.listdir('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/train/images'):
        os.rename(os.path.join('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/train/images', path), os.path.join(main_image_folder, path))
    for path in os.listdir('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/val/images'):
        os.rename(os.path.join('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/val/images', path), os.path.join(main_image_folder, path))
    for path in os.listdir('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/test/images'):
        os.rename(os.path.join('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/alldone/test/images', path), os.path.join(main_image_folder, path))
        
#redirect_to_main_image_folder()