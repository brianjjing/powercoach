import mediapipe as mp
from mediapipe_model_maker import object_detector
import os, time
import tensorflow as tf

model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel.tflite')
coco_path = os.path.join(os.path.dirname(__file__), 'bbelldetecset.coco')
cache_train = os.path.join(os.path.dirname(__file__), 'cachetrain')
cache_valid = os.path.join(os.path.dirname(__file__), 'cachevalid')
cache_test = os.path.join(os.path.dirname(__file__), 'cachetest')

dataset = coco_path
traindataset = os.path.join(dataset, 'train')
print(traindataset)
valdataset = os.path.join(dataset, 'val')
train_data = object_detector.Dataset.from_coco_folder(traindataset, cache_dir=cache_train)
validation_data = object_detector.Dataset.from_coco_folder(valdataset, cache_dir=cache_valid)

#TRADEOFF BETWEEN MEDIAPIPE BARBELL DETECTION MODEL VS YOLO OBJECT DETECTION MODEL:
    #YOLO ACCOUNTS FOR ROTATED BOUNDING BOXES, BUT MEDIAPIPE HAS A BUILT IN DETECT_ASYNC.
    #WITH YOLO, YOU WOULD NEED TO DO ALL THE WORK ASSOCIATED WITH THEREAD HANDLING.
    #PLAN: USE MEDIAPIPE FOR NOW, AND IF IT DOESN'T PRODUCE GOOD BARBELL DETECTION RESULTS OR IS LARGELY INCOMPATIBLE WITH THE FORM ALGS, THEN SWITCH TO YOLO.
    
def export_tflite_model():
    print("Creation starting:")
    #OVERALL:
    #1. MAKE HPARAMS BETTER BASED ON LOGICAL THINKING (DONE)
    #2. FEED BETTER IMAGES (1000) INTO DATASET --> think abt what types of images you need first!
    #3. RETRAIN, OPTIMIZING PARAMETERS ALONG THE WAY WITH SKLEARN --> ALSO SEE HOW YOU CAN DO REDUCELRONPLATEAU, SO COSINE DECAY IS NOT NEEDED ANYMORE
    
    exported_model_path = os.path.join(os.path.dirname(__file__), 'models', 'bbelldetectionmodel')
    num_gpus = len(tf.config.list_physical_devices('GPU'))
    
    spec = object_detector.SupportedModels.MOBILENET_V2 #Best FAST inference: speed is king rn
    model_options = object_detector.ModelOptions(l2_weight_decay = 3e-05)
    hparams = object_detector.HParams(
        learning_rate = 0.005, #Eventually do ReduceLROnPlateau
        batch_size = 16, #How many images at a time are being fed into the model per iteration? However many iterations it takes to get to the full amnt of images in the dataset is the num of steps in an epoch. (Model params changed every batch)
        epochs = 30,
        steps_per_epoch = None,
        class_weights = None,
        shuffle = True,
        #repeat = False,
        export_dir = exported_model_path, #Where intermediate checkpoints and logs are saved
        distribution_strategy = 'off' if num_gpus <= 1 else 'mirrored',
        num_gpus = num_gpus, #Set in stone
        tpu ='', #Not available on AWS, only Google Cloud/Colab and Kaggle
        cosine_decay_epochs = 30,
        cosine_decay_alpha = 0.1
    )
    
    options = object_detector.ObjectDetectorOptions(
        supported_model=spec,
        model_options = model_options, #Optimize the l2_weight_decay regularization parameter
        hparams=hparams #Optimize hparams, using logic first then sklearn
    )
    
    #FOR FUTURE PARAMETER IMPROVEMENT:
    #1. QUANTIZATION AWARE TRAINING?
    #2. REDUCE LR ON PLATEAU? (would just set the learning rate to 0.001 and NO cosine_decay_epochs and cosine_decay_alpha=1

    #WHEN FEEDING DATASET TRAINING IMAGES:
    #1. TURN IMAGES INTO REQUIRED INPUT SIZE? (256X256)
    #2. Worry abt diff types of variation, as well as no barbell pics?
    
    model = object_detector.ObjectDetector.create( #These are alr all 3 parameters
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

#export_tflite_model()

bbell_detector_model = None
barbell_bounding_box = None
#IN DEPLOYMENT, JUST Have this function run, as the model is already exported:
def create_bbell_detection_model():
    BaseOptions = mp.tasks.BaseOptions
    ObjectDetector = mp.tasks.vision.ObjectDetector
    ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    def output_detection_details(result, output_image: mp.Image, timestamp_ms: int):
        # Iterate through detections to find if any category is "barbell"
        for detection in result.detections:
            global barbell_bounding_box
            barbell_bounding_box = None
            if detection.categories:
                #print(f"Barbell detected with confidence: {detection.categories[0].score:.2f}")
                barbell_bounding_box = detection.bounding_box
    
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

bbell_detector_model = create_bbell_detection_model()

start_time = time.time()
for i in range(251):
    try:
        print('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all/images/' + str(i+1) + '.jpg')
        bbell_detector_model.detect_async(mp.Image.create_from_file('/Users/brian/Documents/Python/PowerCoach/powercoachapp/bbelldetecset.coco/all/images/' + str(i+1) + '.jpg'), timestamp_ms=int((time.time() - start_time) * 1000))
        print(barbell_bounding_box)
    except Exception as e:
        print(f"Error while detecting: {e}")
    #time.sleep(0.05) #For allowing the output to come out before the background thread is killed