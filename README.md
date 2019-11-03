# Posture-Advisor
A small tool which observes the sitting posture via webcam and gives visual feedback 
about the quality of a healthy sitting posture.

Machine Learning via Tensorflow is used to achieve this. 

## A brief description
Tensorflow is used in two passes with two different models to evaluate 

1. the human posture (Feature Extraction) and 
2. the quality (Quality Estimation) of a sitting posture. 

### Feature Extraction
In order not to start from scratch, Tensorflow Model
[PoseNet](https://github.com/tensorflow/tfjs-models/tree/master/posenet) is used as a 
fancy feature detector for human postures. Its already pretrained. Features are in form
of a vector which contains scores and positions of human body parts.

### Quality Estimation
The features (the skeleton of the posture) is drawn to 256x256 RGB image and feed into a CNN which evaluates 
the quality of the sitting pose by 6 categories. 
* 0 no human posture at all
* 1 very bad posture
* 2 bad posture
* 3 average posture
* 4 good posture
* 5 very good posture

To train the second tensorflow model we need to provide prerecorded/labeld data set:

### Providing a data set for training
Providing a data set for training is a two step process:

#### Record 
Posture-Advisor contains recording-functionality which just saves raw images from 
webcam. Images are saved with unique names into the folder 'record'.

#### Label
The previously recorded images will labeled with quality attribute (1-5 stars, or None) which is
stored as EXIF tag inside the JPG. Images which were succesfully labeled will
be moved to folder 'label'.


## Install
You need to install at least the following prerequisites:

* Python 3.7
* PySide2 5.13.1                        ```pip install pyside2==5.13.1```
* OpenCV 4.1.1.26                       ```pip install opencv-python==4.1.1.26```
* Tensorflow 2.0.0                      ```pip install tensorflow==2.0.0```
* Numpy 1.16.4                          ```pip install numpy==1.16.4```
* piexif 1.1.3                          ```pip install piexif==1.1.3```


## Usage

* run the app by ```python postureadvisor.py```
* [record] create data set by recording pictures of good/bad sitting postures
* [label] label the quality of sitting postures in the previously created images
* [train] start training the second tensorflow model, provide the number of epochs
* [save model] save the trained model (outputfolder 'posturequalitynetmodel')

### Credits

The PoseNet-Python implementation by Ross Wightman can be found at https://github.com/rwightman/posenet-python

The original PoseNet model, weights, code, etc. was created by Google and can be found at https://github.com/tensorflow/tfjs-models/tree/master/posenet

### Nice to have / Nice to try out
* feed features directly into a MLP, without drawing on image plane
* or instead: transfer learning for PoseNet to train custom features
* add more options to train the quality estimation 
* try PoseNet with ResNet50 
* refactor PoseNet to use Tensorflow2.0 API
* tbc.

