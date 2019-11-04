import sys

from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from PySide2.QtCore import QFile, Signal, QObject, Qt, QThread, Slot, QTimer, QCoreApplication, QRect, QDateTime
from PySide2.QtGui import QImage, QPixmap

# import generated pyUI file
from ui_mainwindow import Ui_MainWindow
from ui_mainwindowtraining import Ui_MainWindowTraining

from imageacquisition import ImageAcquisition
from imagerecorder import ImageRecorder
from imagelabeler import ImageLabeler

from posenet import posenet
import posturequalitynet
import numpy as np
import argparse


class AbstractMainWindow(QMainWindow):
    def __init__(self, image_acq, image_rec, posenet, posture_quality_net):
        super(AbstractMainWindow, self).__init__()
        self.image_acquisition = image_acq
        self.image_recorder = image_rec

        self.posenet = posenet
        self.posture_quality_net = posture_quality_net

    def setup_frame_rendering(self):
        # setup webcam image preview with alpha blended posture
        self.image_acquisition.signal.connect(self.posenet.get_blended_pose_from_image)
        self.posenet.image_blended_signal.connect(self.on_receive_frame)

    @Slot(list)
    def on_receive_frame(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.ui.frame_label.setPixmap(QPixmap.fromImage(q_img))


# setup a simple UI
class MainWindow(AbstractMainWindow):
    def __init__(self, image_acq, image_rec, posenet, posture_quality_net):
        super(MainWindow, self).__init__(image_acq, image_rec, posenet, posture_quality_net)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def setup_prediciton(self):
        self.posture_quality_net.load_model()
        self.posenet.image_skeleton_signal.connect(self.posture_quality_net.predict_on_skeleton_image)
        self.posture_quality_net.predicition_signal.connect(self.on_prediciton)

    @Slot(int)
    def on_prediciton(self, prediciton):
        if prediciton == 0:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#1538e8;">No Posture</span></p></body></html>')
        if prediciton == 1:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#e81515;">Very Bad Posture</span></p></body></html>')
        if prediciton == 2:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#e87b15;">Bad Posture</span></p></body></html>')
        if prediciton == 3:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#e8d615;">Average Posture</span></p></body></html>')
        if prediciton == 4:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#a2e815;">Good Posture</span></p></body></html>')
        if prediciton == 5:
            self.ui.label.setText(
                '<html><head/><body><p><span style=" font-size:18pt; color:#15e827;">Very Good Posture</span></p></body></html>')


# setup a simple UI for training
class MainWindowTraining(AbstractMainWindow):
    def __init__(self, image_acq, image_rec, posenet, posture_quality_net):
        super(MainWindowTraining, self).__init__(image_acq, image_rec, posenet, posture_quality_net)

        self.ui = Ui_MainWindowTraining()
        self.ui.setupUi(self)

        # setup buttons
        self.ui.record_button.clicked.connect(self.on_record_button)
        self.ui.label_button.clicked.connect(self.on_label_button)
        self.ui.train_button.clicked.connect(self.on_train_button)
        self.ui.test_button.clicked.connect(self.on_test_button)
        self.ui.load_model_button.clicked.connect(self.on_load_model_button)
        self.ui.save_model_button.clicked.connect(self.on_save_model_button)

    # this method will be called when record start button is pressed
    def on_record_button(self):
        if self.ui.record_button.text() == "Start":
            record_time_in_s = self.ui.timeEdit.dateTime().toSecsSinceEpoch()
            cycle_time_in_s = self.ui.spinBox.value()
            self.image_recorder.start(record_time_in_s, cycle_time_in_s)
            self.image_recorder.timeout.connect(self.on_record_button)
            self.ui.record_button.setText("Stop")
        else:
            self.image_recorder.stop()
            self.ui.record_button.setText("Start")

    # this method will be called when label start button is pressed
    def on_label_button(self):
        image_labeler = ImageLabeler("record", "label", self)
        image_labeler.show()

    def on_train_button(self):
        self.posture_quality_net.train(self.ui.spinBox_2.value())

    def on_test_button(self):
        frame = self.image_acquisition.read_frame()
        value = self.posture_quality_net.predict_on_raw_image(frame)
        self.ui.lcdNumber.display(value)

    def on_load_model_button(self):
        self.posture_quality_net.load_model()

    def on_save_model_button(self):
        self.posture_quality_net.save_model()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true')
    args = parser.parse_args()

    app = QApplication([])

    image_acquisition = ImageAcquisition()
    image_recorder = ImageRecorder(image_acquisition.read_frame, "record")

    posenet = posenet.PoseNet()
    posture_quality_net = posturequalitynet.PostureQualityNet(posenet)

    if args.train:
        main_window_training = MainWindowTraining(image_acquisition, image_recorder, posenet, posture_quality_net)
        main_window_training.setup_frame_rendering()
        main_window_training.show()
    else:
        main_window = MainWindow(image_acquisition, image_recorder, posenet, posture_quality_net)
        main_window.setup_frame_rendering()
        main_window.setup_prediciton()
        main_window.show()

    r = app.exec_()
    sys.exit(r)
