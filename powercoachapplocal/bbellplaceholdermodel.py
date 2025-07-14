import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from powercoachapplocal.extensions import shared_data

# STEP 2: Create an ObjectDetector object.
VisionRunningMode = mp.tasks.vision.RunningMode
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    if result.detections:
        for detection in result.detections:
            if detection.categories[0].category_name == 'skateboard':
                print(detection)
                shared_data['bar_bbox'] = detection.bounding_box
                print(shared_data['bar_bbox'])
                
                #bounding_box=BoundingBox(origin_x=..., origin_y=..., width=..., height=...
                break
            else:
                print(detection.categories[0].category_name)
    #Don't be so strict yet:
    # else:
    #     shared_data['bar_bbox'] = None #Maybe don't be so strict with it ... make a counter or smth every time it disappears, and only reset it to None when the counter reaches 1 sec
    #     shared_data['deadlift_stage'] = 1
    #     shared_data['message'] = "BARBELL NOT IN FRAME"
    
    #For computer:
    # if shared_data['bar_bbox']:
    #     start_point = (int(shared_data['bar_bbox'].origin_x), int(shared_data['bar_bbox'].origin_y))  # top-left corner
    #     end_point = (int(shared_data['bar_bbox'].origin_x + shared_data['bar_bbox'].width),
    #                 int(shared_data['bar_bbox'].origin_y + shared_data['bar_bbox'].height))
    #     cv2.rectangle(shared_data['original_frame'], start_point, end_point, color=(255,0,0), thickness=2)
    
base_options = python.BaseOptions(model_asset_path='/Users/brian/Documents/Python/PowerCoach/powercoachapp/models/efficientdet_lite0.tflite')
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       running_mode=VisionRunningMode.LIVE_STREAM,
                                        max_results=5,
                                       score_threshold=0.01,
                                       result_callback=print_result)

bar_detector_model = vision.ObjectDetector.create_from_options(options)

#HORIZONTAL BAR DETECTION MODEL: