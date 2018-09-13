import os
import time
import tarfile
import six.moves.urllib as urllib
import threading
import cv2
import numpy as np
import tensorflow as tf
from .match import *
import glob as gb
from .utils.ssd_mobilenet_utils import *
from PIL import Image


class model:
    def __init__(self):
        self.object_save = []
        self.tracking_save = []
        self.type_save = []
        #object
        self.object_num = 0
        # some global data
        self.out_scores = []
        self.out_boxes = []
        self.out_classes = [] 
        self.class_names = [] 
        self.colors = []

    def trans(self, image):
        imgRGB = cv2.cvtColor (image, cv2.IMREAD_COLOR)
        r, buf = cv2.imencode (".jpg", imgRGB)
        bytes_image =Image.fromarray (np.uint8 (buf)).tobytes ()
        return bytes_image

    def object_detection(self, image, image_data, sess):

        image_tensor = sess.graph.get_tensor_by_name('image_tensor:0')

        detection_boxes = sess.graph.get_tensor_by_name('detection_boxes:0')
               
        detection_scores = sess.graph.get_tensor_by_name('detection_scores:0')
        detection_classes = sess.graph.get_tensor_by_name('detection_classes:0')
        num_detections = sess.graph.get_tensor_by_name('num_detections:0')

        boxes, scores, classes, num = sess.run([detection_boxes, detection_scores, detection_classes, num_detections],
                                                        feed_dict={image_tensor: image_data})
        boxes, scores, classes = np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes).astype(np.int32)
        self.out_scores, self.out_boxes, self.out_classes = non_max_suppression(scores, boxes, classes)

        self.colors = generate_colors(self.class_names)
        image, img, name = draw_boxes(image, self.out_scores, self.out_boxes, self.out_classes, self.class_names, self.colors)
        
        return image, img, name

    def tracking(self, img, image, name):
        h, w, _ = image.shape
        for i in range(len(img)):
            if self.object_num == 0:
                self.object_save.append(img[i])
                self.type_save.append(name[i])
                t = np.zeros((h,w,3),np.uint8)
                self.tracking_save.append(t)
                self.object_num += 1
                continue
            key = 0
            mini = 100000
            num = 0
            center = []
            for j in range(self.object_num):
                diff = getSim(img[i], self.object_save[j])
                if diff < 150 and self.type_save[j] == name[i]:
                    if diff < mini:
                        num = j
                        mini = diff
                    key = 1
                    ymin, xmin, ymax, xmax = self.out_boxes[i]
                    left, right, top, bottom = (xmin * w, xmax * w,
                                              ymin * h, ymax * h)
                    top = max(0, np.floor(top + 0.5).astype('int32'))
                    left = max(0, np.floor(left + 0.5).astype('int32'))
                    bottom = min(h, np.floor(bottom + 0.5).astype('int32'))
                    right = min(w, np.floor(right + 0.5).astype('int32'))  
                    center = [(top+bottom)/2.0, (left+right)/2.0]              
                    break
            if key == 0:
                self.object_save.append(img[i])
                self.type_save.append(name[i])
                t = np.zeros((h,w,3),np.uint8)
                self.tracking_save.append(t)
                self.object_num += 1

            else:
                print(self.type_save[num], name[i])
                cv2.circle(self.tracking_save[num],(int(center[1]),int(center[0])),2,(55,255,155),2)

    def work(self, v_id):

        # What model to download
        model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
        model_file = model_name + '.tar.gz'
        
        # Download model to model_data dir
        model_dir = './model_data'
        if not os.path.isdir(model_dir):
            os.mkdir(model_dir)
        model_path = os.path.join(model_dir, model_file)

        # Untar model
        tar_file = tarfile.open(model_path)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, model_dir)

        # Load a (frozen) Tensorflow model into memory.
        path_to_ckpt = model_dir + '/' + model_name + '/frozen_inference_graph.pb'
        
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.class_names = read_classes('./model_data/coco_classes.txt')

        with detection_graph.as_default():
            with tf.Session() as sess:
                camera = cv2.VideoCapture(v_id)#"rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0")
                img = None
                count = 0
                while camera.isOpened():
                    ret, frame = camera.read() 
                    if ret:
                        image = frame
                        image_data = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        image_data_expanded = np.expand_dims(image_data, axis=0)
                        if count % 5 == 0:
                            count = 0
                            image, img, name = self.object_detection(image, image_data_expanded, sess)
                            self.tracking(img, image, name)
                        else:
                            image, img, name = draw_boxes(image, self.out_scores, self.out_boxes, self.out_classes, self.class_names, self.colors)

                        # send mjpg
                        yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + self.trans(image) + b'\r\n\r\n')

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    count += 1
                camera.release()
                cv2.destroyAllWindows()