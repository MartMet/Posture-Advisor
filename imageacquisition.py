from PySide2.QtCore import Signal, QThread, QObject, QTimer
from PySide2.QtGui import QImage, QPixmap
import cv2
import time
import platform


# singleton which is used to acquire images from USB-webcam via OpenCV
class ImageAcquisition(QObject):
    signal = Signal(list)
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ImageAcquisition.__instance == None:
            ImageAcquisition()
        return ImageAcquisition.__instance

    def __init__(self, parent=None, camera_id=0, resolution_x=640, resolution_y=480, time_in_ms=200):
        QObject.__init__(self, parent)

        # cv2.CAP_DSHOW to ensure compatibility with Windows and DirectShow
        if platform.system() == "Windows":
            self.cap = cv2.VideoCapture(cv2.CAP_DSHOW + camera_id)
        else:
            self.cap = cv2.VideoCapture(camera_id)

        self.img_timer = QTimer(self)
        self.img_timer.setSingleShot(False)
        self.img_timer.timeout.connect(self.read_frame)
        self.img_timer.start(time_in_ms)
        self._x = resolution_x
        self._y = resolution_y
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._x)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._y)

        if ImageAcquisition.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ImageAcquisition.__instance = self

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def read_frame(self):
        ret, frame = self.cap.read()
        self.signal.emit(frame)
        return frame

    def __del__(self):
        self.cap.release()
        print('ImageAcquisition closed')
