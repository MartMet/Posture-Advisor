import tensorflow.compat.v1 as tf
from PySide2.QtCore import Signal, QThread, QObject, QTimer, Slot
import cv2
import numpy as np

import posenet.decode
import posenet.draw

tf.disable_v2_behavior()

GRAPH_PB_PATH = './posenetmodel/model-mobilenet_v1_101.pb'


class PoseNet(QObject):
    image_blended_signal = Signal(list)
    image_skeleton_signal = Signal(list)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.sess = tf.Session()
        self.f = tf.gfile.GFile(GRAPH_PB_PATH, 'rb')
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(self.f.read())
        self.sess.graph.as_default()
        tf.import_graph_def(graph_def, name='')
        self.offsets = self.sess.graph.get_tensor_by_name('offset_2:0')
        self.displacement_fwd = self.sess.graph.get_tensor_by_name('displacement_fwd_2:0')
        self.displacement_bwd = self.sess.graph.get_tensor_by_name('displacement_bwd_2:0')
        self.heatmaps = self.sess.graph.get_tensor_by_name('heatmap:0')

    def __preprocess_image(self, source_img, scale_factor=1.0, output_stride=16):
        target_width, target_height = self.__valid_resolution(
            source_img.shape[1] * scale_factor, source_img.shape[0] * scale_factor, output_stride=output_stride)
        scale = np.array([source_img.shape[0] / target_height, source_img.shape[1] / target_width])

        input_img = cv2.resize(source_img, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB).astype(np.float32)
        input_img = input_img * (2.0 / 255.0) - 1.0
        input_img = input_img.reshape(1, target_height, target_width, 3)
        return input_img, source_img, scale

    def __valid_resolution(self, width, height, output_stride=16):
        target_width = (int(width) // output_stride) * output_stride + 1
        target_height = (int(height) // output_stride) * output_stride + 1
        return target_width, target_height

    # does return a alpha blended pose with the original image and the image with the skeleton
    @Slot(list)
    def get_blended_pose_from_image(self, image):
        res = self.get_pose_from_image(image)
        image_skeleton = res[3]
        image_blended = cv2.addWeighted(image, 1, image_skeleton, 1, 0);
        self.image_skeleton_signal.emit(image_skeleton)
        self.image_blended_signal.emit(image_blended)
        return image_blended, image_skeleton

    def get_pose_from_image(self, image):
        input_image, source_image, scale = self.__preprocess_image(image)
        heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = self.sess.run(
            [self.heatmaps, self.offsets, self.displacement_fwd, self.displacement_bwd],
            feed_dict={'image:0': input_image}
        )
        pose_scores, keypoint_scores, keypoint_coords = posenet.decode.decode_multiple_poses(
            heatmaps_result.squeeze(axis=0),
            offsets_result.squeeze(axis=0),
            displacement_fwd_result.squeeze(axis=0),
            displacement_bwd_result.squeeze(axis=0),
            output_stride=16,
            max_pose_detections=1,
            min_pose_score=0.005)
        empty_image = np.zeros(image.shape, dtype=image.dtype)
        image_skeleton = posenet.draw.draw_skel_and_kp(empty_image, pose_scores, keypoint_scores, keypoint_coords,
                                                       min_pose_score=0.005,
                                                       min_part_score=0.005)
        #cv2.imshow('skel', image)
        return pose_scores, keypoint_scores, keypoint_coords, image_skeleton
