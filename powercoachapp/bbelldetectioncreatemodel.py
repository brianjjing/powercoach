import mediapipe as mp
import os
from flask import session
from powercoachapp.extensions import logger, active_form_correctors

"""
Eventually just deploy this to the cloud since its stateless, and get from there:
"""

model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')

#IN DEPLOYMENT, JUST Have this function run, as the model is already exported:
def create_bbell_detection_model():
    BaseOptions = mp.tasks.BaseOptions
    ObjectDetector = mp.tasks.vision.ObjectDetector
    ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    def output_detection_details(result, output_image: mp.Image, timestamp_ms: int):
        logger.info("barbell detection model result callback - firing and forgetting:")
        #Testing if smth was actually detected - firing and forgetting:
        if result.detections:
            logger.info("Detections:")
            session['bbell_bbox'] = result.detections[0].bounding_box
            logger.info(f"Detection: {session['bbell_bbox']}")
            session['confidence'] = result.detections[0].categories[0].score
            logger.info(f"Confidence: {session['confidence']}")
        else:
            logger.info("Detections:")
            session['bbell_bbox'] = None
            session['confidence'] = 0
            logger.info("No barbell detections")
    
    options = ObjectDetectorOptions(
        base_options = BaseOptions(model_asset_path=model_path),
        running_mode = VisionRunningMode.LIVE_STREAM,
        #display_names_locale = 'en', #Already made english by default
        max_results = 5,
        score_threshold = 0.001,
        category_allowlist = ['Barbell'], #Only detects barbells
        result_callback = output_detection_details
    )

    bbell_detector = ObjectDetector.create_from_options(options)
    #Problem: Low asf recall and precision, but mainly low asf recall. It can't detect a good QUANTITY of barbells, but of the barbells it detects, the QUALITY of detections was decent (decent amnt of things it detected were actually barbells)
    
    return bbell_detector

# def get_average_iou():
#   import time
#   import cv2 as cv

#     def yolo_to_yolo_box(yolo_coords, img_width, img_height):
#         center_x, center_y, box_width, box_height = yolo_coords
        
#         # Un-normalize coordinates
#         abs_center_x = center_x * img_width
#         abs_center_y = center_y * img_height
#         abs_width = box_width * img_width
#         abs_height = box_height * img_height

#         # Convert to origin_x, origin_y, width, height
#         origin_x = int(abs_center_x - (abs_width / 2))
#         origin_y = int(abs_center_y - (abs_height / 2))

#         #{'origin_x': origin_x, 'origin_y': origin_y, 'width': int(abs_width), 'height': int(abs_height)}
#         return [origin_x, origin_y, int(abs_width), int(abs_height)]

#     def calculate_iou(yolo_box, bbell_detection_box):
#         bbell_detection_box = [bbell_detection_box.origin_x, bbell_detection_box.origin_y, bbell_detection_box.width, bbell_detection_box.height]
        
#         # Determine the coordinates of the intersection rectangle
#         x_inter1 = max(yolo_box[0], bbell_detection_box[0])
#         y_inter1 = max(yolo_box[1], bbell_detection_box[1])
#         x_inter2 = min(yolo_box[0] + yolo_box[2], bbell_detection_box[0] + bbell_detection_box[2])
#         y_inter2 = min(yolo_box[1] + yolo_box[3], bbell_detection_box[1] + bbell_detection_box[3])

#         # Calculate the area of intersection
#         inter_width = max(0, x_inter2 - x_inter1)
#         inter_height = max(0, y_inter2 - y_inter1)
#         intersection_area = inter_width * inter_height

#         # Calculate the area of both bounding boxes
#         yolo_box_area = yolo_box[2] * yolo_box[3]
#         bbell_detection_box_area = bbell_detection_box[2] * bbell_detection_box[3]
        
#         # Calculate the area of union
#         union_area = float(yolo_box_area + bbell_detection_box_area - intersection_area)
        
#         # Avoid division by zero
#         if union_area == 0:
#             return 0.0

#         # Return the IoU
#         iou = intersection_area / union_area
#         return iou
    
#     val_image_pathway = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/val/images'
#     val_labels_pathway = '/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/val/labels'
#     start_time = time.time()

#     total_iou = 0
#     current_iter = 0

#     for bbell_image_dir in os.listdir(val_image_pathway):
#         img_pathway = os.path.join(val_image_pathway, bbell_image_dir)
#         label_pathway = os.path.join(val_labels_pathway, f'{bbell_image_dir[:-3]}txt')
        
#         img = cv.cvtColor(cv.imread(img_pathway), cv.COLOR_BGR2RGB)
#         mpframe = mp.Image(mp.ImageFormat.SRGB, data=img)
        
#         bbell_detector_model.detect_async(mpframe, int(1000*(time.time() - start_time)))
#         time.sleep(0.05)
#         print(session['bar_bbox'])
        
#         with open(label_pathway, 'r') as yolo_file:
#             yolo_first_detection = yolo_file.readline()
#             yolo_first_detection_list = yolo_first_detection.split()
#             yolo_first_detection_list = [float(num) for num in yolo_first_detection_list]
#             try:
#                 yolo_box = yolo_to_yolo_box(yolo_first_detection_list[1:5], session['frame_width'], session['frame_height'])
#                 current_iter+=1
#             except ValueError: #Where the testing dataset had no yolo box. Skipping this, as we can't inflate the iou by adding 1.0 each time.
#                 continue
#             print(yolo_box)
#             if session['bar_bbox']:
#                 iou = calculate_iou(yolo_box, session['bar_bbox'])
#             else:
#                 iou = 0.0
#             print(iou)
#             total_iou+=iou
            
        
#     print("TOTAL IoU: ", total_iou)
#     print("CURRENT ITER: ", current_iter)
#     print("AVERAGE IoU: ", total_iou/current_iter)