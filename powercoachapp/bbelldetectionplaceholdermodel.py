import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from powercoachapp.extensions import shared_data, logger

# STEP 2: Create an ObjectDetector object.
VisionRunningMode = mp.tasks.vision.RunningMode
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    if result.detections:
        for detection in result.detections:
            if detection.categories[0].category_name == 'skateboard':
                logger.info("Detection: \n", detection)
                shared_data['bar_bbox'] = detection.bounding_box
                logger.info("Bounding box of detection: \n", shared_data['bar_bbox'])
                break
            else:
                logger.info("Objects detected in frame: \n", detection.categories[0].category_name)
    
base_options = python.BaseOptions(model_asset_path=os.path.join(os.path.dirname(__file__), 'models', 'efficientdet_lite0.tflite'))
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       running_mode=VisionRunningMode.LIVE_STREAM,
                                        max_results=5,
                                       score_threshold=0.01,
                                       result_callback=print_result)

bbell_detection_model = vision.ObjectDetector.create_from_options(options)