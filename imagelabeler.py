from PySide2.QtCore import Signal, QThread, QObject, QTimer
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QMessageBox, QPushButton, QDialog
import os
import glob
import shutil
import exifmetadata

# import generated pyUI file
from ui_imagelabeler import Ui_Dialog


# a simple Dialog to label previously recorded images into good/bad/no posture
class ImageLabeler(QDialog):
    def __init__(self, subfolder_in, subfolder_out, parent=None):
        super(ImageLabeler, self).__init__(parent)
        self.subfolder_in = subfolder_in
        self.subfolder_out = subfolder_out
        self.setModal(True)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # create subfolder if not present
        if os.path.isdir(subfolder_out) == False:
            os.mkdir(subfolder_out)
        self.image_file_paths = glob.glob(os.path.join(self.subfolder_in, '**', '*.jpg'), recursive=True)
        self.image_max_count = len(self.image_file_paths)

        # adapt progressbar max. to amount of files in record folder
        self.ui.progressBar.setMaximum(self.image_max_count)
        self.ui.progressBar.setMinimum(0)

        # connect buttons
        self.ui.set_label_button.clicked.connect(self.on_set_label_button)
        self.ui.set_label_button_no_posture.clicked.connect(self.on_set_label_no_posture_button)
        self.ui.skip_button.clicked.connect(self.on_skip_button)

        # connect dial to lcd number
        self.ui.dial.valueChanged.connect(self.ui.lcdNumber.display)

        self.show_next_image()

    # action performed when "set label" button is pressed
    def on_set_label_button(self):
        self.__on_button_action(True, self.ui.dial.value())

    # action performed when "set label no posture" button is pressed
    def on_set_label_no_posture_button(self):
        self.__on_button_action(True, None)

    # action performed when "skip" button is pressed
    def on_skip_button(self):
        self.__on_button_action(False, None)

    def __on_button_action(self, write_exif, value):
        try:
            image_file_path = self.image_file_paths.pop(0)
            if write_exif is True:
                self.label_image(image_file_path, value)
        except IndexError:
            self.close()
            return
        self.show_next_image()

    # shows up the next image and updates the progessbar
    def show_next_image(self):
        if len(self.image_file_paths) is 0:
            return
        self.ui.frame_label.setPixmap(QPixmap(self.image_file_paths[0]))
        self.ui.progressBar.setValue(self.image_max_count - len(self.image_file_paths))

    def label_image(self, image_file_path, label_data):
        rel = os.path.relpath(image_file_path, self.subfolder_in)
        new_image_file_path = os.path.join(self.subfolder_out, rel)
        shutil.move(image_file_path, new_image_file_path)
        exifmetadata.write_exif_tag_rating(new_image_file_path, label_data)

    def keyPressEvent(self, event):
        # 1
        if event.key() == 49:
            self.ui.dial.setValue(1)
            self.on_set_label_button()
        # 2
        if event.key() == 50:
            self.ui.dial.setValue(2)
            self.on_set_label_button()
        # 3
        if event.key() == 51:
            self.ui.dial.setValue(3)
            self.on_set_label_button()
        # 4
        if event.key() == 52:
            self.ui.dial.setValue(4)
            self.on_set_label_button()
        # 5
        if event.key() == 53:
            self.ui.dial.setValue(5)
            self.on_set_label_button()
        # enter key -> set quality label
        if event.key() == 16777220:
            self.on_set_label_button()
        # escape key -> skip image
        if event.key() == 16777216:
            self.on_skip_button()
        # space key -> set no label
        if event.key() == 32:
            self.on_set_label_no_posture_button()
