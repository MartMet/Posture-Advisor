import tensorflow as tf
from tensorflow.keras import datasets, layers, models

from PySide2.QtCore import Signal, QThread, QObject, QTimer, Slot

import glob
import os
import cv2
import numpy as np
import exifmetadata


class PostureQualityNet(QObject):
    predicition_signal = Signal(int)

    def __init__(self, feature_detector, source_dir="label", parent=None):
        QObject.__init__(self, parent)
        self.input_img_xy = 256
        self.model = models.Sequential()
        self.model.add(
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.input_img_xy, self.input_img_xy, 3)))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((2, 2)))
        self.model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(64, activation='relu'))
        self.model.add(layers.Dense(6, activation='softmax'))
        print(self.model.summary())
        self.model.compile(optimizer='adam',
                           loss='sparse_categorical_crossentropy',
                           metrics=['accuracy'])
        self.source_dir = source_dir
        self.feature_detector = feature_detector

        # create output dir for posturequalitynetmodel
        if os.path.isdir("posturequalitynetmodel") == False:
            os.mkdir("posturequalitynetmodel")

    def __prepare_traindata(self):
        image_file_paths = glob.glob(os.path.join(self.source_dir, '**', '*.jpg'), recursive=True)
        if not image_file_paths:
            raise ValueError("no labeled images available, please record and label some images first!")
        data_input_array = None
        data_output_array = None
        print("start prepare train data")
        for idx, image_file_path in enumerate(image_file_paths):
            print("prepare sample image " + str(idx))

            # first part convert all labeled images to one big array
            img = cv2.imread(image_file_path)
            res = self.feature_detector.get_pose_from_image(img)
            img = cv2.resize(res[3], (self.input_img_xy, self.input_img_xy), interpolation=cv2.INTER_AREA)
            img = img.astype(np.float32)
            img_max = img.max()
            if img_max != 0:
                img *= 255.0 / img_max

            if data_input_array is None:
                data_input_array = np.expand_dims(img, axis=0)
            else:
                data_input_array = np.vstack([data_input_array, np.expand_dims(img, axis=0)])

            rating_value = exifmetadata.read_exif_tag_rating(image_file_path)
            if rating_value is None:
                rating_value = 0

            if data_output_array is None:
                data_output_array = np.expand_dims(rating_value, axis=0)
            else:
                data_output_array = np.vstack([data_output_array, np.expand_dims(rating_value, axis=0)])
        return data_input_array, data_output_array

    def train(self, epochs=5):
        train_images, train_labels = self.__prepare_traindata()
        self.model.fit(train_images, train_labels, epochs=epochs)


    def predict_on_raw_image(self, img):
        # detect skeleton image (features) first
        res = self.feature_detector.get_pose_from_image(img)
        self.vanilla_predict(res[3])

    @Slot(list)
    def predict_on_skeleton_image(self, img):
        img = cv2.resize(img, (self.input_img_xy, self.input_img_xy), interpolation=cv2.INTER_AREA)
        #cv2.imshow('pred', img)
        img = img.astype(np.float32)
        img_max = img.max()
        if img_max != 0:
            img *= 255.0 / img_max
        prediction_array = self.model.predict(np.expand_dims(img, axis=0))
        prediction = np.argmax(prediction_array)

        self.predicition_signal.emit(prediction)
        return prediction

    def save_model(self):
        self.model.save_weights('./posturequalitynetmodel/posturequalitynet')

    def load_model(self):
        try:
            self.model.load_weights('./posturequalitynetmodel/posturequalitynet')
        except tf.errors.NotFoundError:
            raise ValueError("no Model found for quality estimation, please train a Model first")
