import tensorflow as tf
import tensorflow_datasets as tfds
import fiftyone as fo
import fiftyone.zoo as foz

dataset = foz.load_zoo_dataset(
    "coco-2017",
    split="train",
    label_types=["detections"],
    classes=["skateboard"]
)

session = fo.launch_app(dataset, port=1234)
session.wait()

# dataset = tfds.load('open_images_v4', split='train')
# for datum in dataset:
#   image, bboxes = datum["image"], example["bboxes"]