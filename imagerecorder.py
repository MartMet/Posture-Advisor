from PySide2.QtCore import Signal, QThread, QObject, QTimer
from PySide2.QtGui import QImage, QPixmap
import cv2
import time
from datetime import datetime
import os


class ImageRecorder(QObject):
    def __init__(self, get_frame_func, subfolder, parent=None):
        QObject.__init__(self, parent)
        self.get_frame_func = get_frame_func
        self.period_timer = QTimer(self)
        self.duration_timer = QTimer(self)
        self.subfolder = subfolder
        # create subfolder if not present
        if os.path.isdir(subfolder) == False:
            os.mkdir(subfolder)

    def start(self, time_duration_in_s, time_period_in_s):
        self.time_duration_in_s = time_duration_in_s
        self.time_period_in_s = time_period_in_s
        self.period_timer.setSingleShot(False)
        self.period_timer.timeout.connect(self.read_frame)
        self.period_timer.start(self.time_period_in_s * 1000)

        self.duration_timer.setSingleShot(True)
        self.duration_timer.timeout.connect(self.period_timer.stop)
        self.duration_timer.start(self.time_duration_in_s * 1000)

    def stop(self):
        self.period_timer.stop()
        self.duration_timer.stop()
        # disconnect all
        QObject.disconnect(self.period_timer)
        QObject.disconnect(self.duration_timer)

    @property
    def timeout(self):
        return self.duration_timer.timeout

    # cyclic started reading of frames
    def read_frame(self):
        unique_filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        frame = self.get_frame_func()
        cv2.imwrite(self.subfolder + '/' + unique_filename + '.jpg', frame)
