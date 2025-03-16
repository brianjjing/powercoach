#FIXING THE NO MODULE NAMED POWERCOACHAPP ERROR:
import sys
sys.path.append("/Users/brian/Documents/Python/PowerCoach")

import cv2
import mediapipe_model_maker
from mediapipe_model_maker import object_detector
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector
print('importing starting:')
from powercoachapp.bbelldetectionbbox import bbellbbox, drawbbox
from powercoachapp.poselandmarkalgs import drawlandmarks
print('importing done')

path = '/Users/brian/Downloads/Screenshot 2025-01-02 at 11.55.09 AM.png'
bbox = bbellbbox(path)
print(bbox)
drawbbox(path, bbox)

"""path = '/Users/brian/Downloads/DEADY.jpeg'

# Reading an image in default mode
image = cv2.imread(path)
print(type(image))
print(image)
print(image.shape)

# Window name in which image is displayed
window_name = 'image'

# Using cv2.imshow() method
# Displaying the image
cv2.imshow(window_name, image)

# waits for user to press any key
# (this is necessary to avoid Python kernel form crashing)
cv2.waitKey(0)
cv2.destroyAllWindows()"""

#FIND OUT HOW TO LOAD IN THE DAMN MODEL.
"""
#print(dir(object_detector.ObjectDetector))
bbellmodel = object_detector.ObjectDetector(
    model_spec = object_detector.ModelSpec(
        downloaded_files = mediapipe_model_maker.face_stylizer.constants.file_util.DownloadedFiles(
            path = '/Users/brian/Documents/Python/PowerCoach/models/bbelldetectionmodel',
            url = '/Users/brian/Downloads/bbelldetectionmodel.tar.gz',
            is_folder = True
        ), 
        checkpoint_name = 'float_ckpt',
        input_image_shape = [256, 256, 3],
        model_id = 'MobileNetV2',
        min_level = 3,
        max_level = 7
    ),
    label_names = ['Barbell'],
    hparams = object_detector.HParams,
    model_options = object_detector.ModelOptions()
)

print(dir(bbellmodel))
print(bbellmodel.summary)
"""
