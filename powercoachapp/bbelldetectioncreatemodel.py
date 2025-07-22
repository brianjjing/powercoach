import mediapipe as mp
import time, os
import cv2 as cv

model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')

#IN DEPLOYMENT, JUST Have this function run, as the model is already exported:
def create_bbell_detection_model():
    BaseOptions = mp.tasks.BaseOptions
    ObjectDetector = mp.tasks.vision.ObjectDetector
    ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    def output_detection_details(result, output_image: mp.Image, timestamp_ms: int):
        print("RESULT CALLBACK: ")
        global barbell_bounding_box
        barbell_bounding_box = None #Just make it so that the barbell is forced to refresh every few frames, as opposed to making it none every time
        if result.detections:
            print("Detections:")
            barbell_bounding_box = result.detections[0].bounding_box
            print(f"Detection: {barbell_bounding_box}")
            print(f"Confidence: {result.detections[0].categories[0].score}")
        else:
            print("No barbell detections")
    
    options = ObjectDetectorOptions(
        base_options = BaseOptions(model_asset_path=model_path),
        running_mode = VisionRunningMode.LIVE_STREAM,
        #display_names_locale = 'en', #Already made english by default
        max_results = 5,
        score_threshold = 0.01, #Retrain with lower score threshold.
        category_allowlist = ['Barbell'], #Only detects barbells
        result_callback = output_detection_details
    )

    bbell_detector = ObjectDetector.create_from_options(options)
    #Problem: Low asf recall and precision, but mainly low asf recall. It can't detect a good QUANTITY of barbells, but of the barbells it detects, the QUALITY of detections was decent (decent amnt of things it detected were actually barbells)
    
    return bbell_detector

bbell_detector_model = create_bbell_detection_model()

#Put this in the bbox file:
def detect_in_image(path):
    start_time = time.time()
    image = mp.Image.create_from_file(path)

    print("IMAGE: ", image)
    bbell_detector_model.detect_async(image, timestamp_ms=int((time.time() - start_time) * 1000))
    time.sleep(1)

    image_np = image.numpy_view()
    image_bgr = cv.cvtColor(image_np, cv.COLOR_RGB2BGR)
    cv.rectangle(image_bgr, (barbell_bounding_box.origin_x, barbell_bounding_box.origin_y), (barbell_bounding_box.origin_x+barbell_bounding_box.width, barbell_bounding_box.origin_y+barbell_bounding_box.height), (255,0,0), 2)
    cv.imshow("Detected Image", image_bgr)
    cv.waitKey(0)
    cv.destroyAllWindows()    
detect_in_image('/Users/brian/Downloads/man-working-out-in-a-gym-with-barbell-and-weights-royalty-free-image-1694172345.avif')