import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django
django.setup()
from news.models import New
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
from django.utils import timezone

close_thread = 0


# preload model
# What model to download
model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
model_file = model_name + '.tar.gz'

# Download model to model_data dir
model_dir = './model_data'
if not os.path.isdir(model_dir):
    os.mkdir(model_dir)
model_path = os.path.join(model_dir, model_file)

# Load a (frozen) Tensorflow model into memory.
path_to_ckpt = model_dir + '/' + model_name + '/frozen_inference_graph.pb'

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

with detection_graph.as_default():
    sess = tf.Session()
    image = cv2.imread('init.png')
    image_data = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_data_expanded = np.expand_dims(image_data, axis=0)
    image_tensor = sess.graph.get_tensor_by_name('image_tensor:0')

    detection_boxes = sess.graph.get_tensor_by_name('detection_boxes:0')
           
    detection_scores = sess.graph.get_tensor_by_name('detection_scores:0')
    detection_classes = sess.graph.get_tensor_by_name('detection_classes:0')
    num_detections = sess.graph.get_tensor_by_name('num_detections:0')

    boxes, scores, classes, num = sess.run([detection_boxes, detection_scores, detection_classes, num_detections],
                                                    feed_dict={image_tensor: image_data_expanded})


show_id = 0
def change_channel():
    global show_id
    show_id = 1-show_id

def get_channel():
    global show_id
    return show_id


def change_status():
    global close_thread
    close_thread = 1-close_thread

def get_status():
    global close_thread
    return close_thread

def judge_alarm(left, right, top, bottom, center, video_id, name):
    if center[1] > left and center[1] < right and center[0] < bottom and center[0] > top:
        alarm = name + " be in dangerous area (" + str(left) + "," + str(right) + "," + str(bottom) + "," +str(top) + ")" + ' with '+'('+str(center[1])+ ','+str(center[0]) + ')'
        n = New(news_title = alarm, news_date = timezone.now(), news_type = video_id)
        n.save()

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
        self.class_names = read_classes('./model_data/coco_classes.txt')
        self.colors = []

    # encode
    def trans(self, image):
        imgRGB = cv2.cvtColor (image, cv2.IMREAD_COLOR)
        r, buf = cv2.imencode (".jpg", imgRGB)
        bytes_image =Image.fromarray (np.uint8 (buf)).tobytes ()
        return bytes_image

    # use model
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

    # tracking person with match
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
                    label = '{}'.format("id"+str(num+1))
                    font_face = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1
                    font_thickness = 2

                    label_size = cv2.getTextSize(label, font_face, font_scale, font_thickness)[0]
                    label_rect_left, label_rect_top = int(left - 3), int(top - 3)
                    label_rect_right, label_rect_bottom = int(left + 3 + label_size[0]), int(top - 5 - label_size[1])
                    cv2.putText(image, label, (left, int(top - 4)), font_face, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)
                    break
            if key == 0:
                self.object_save.append(img[i])
                self.type_save.append(name[i])
                t = np.zeros((h,w,3),np.uint8)
                self.tracking_save.append(t)
                self.object_num += 1
            else:
                cv2.circle(self.tracking_save[0],(int(center[1]),int(center[0])),2,((47*num)%256,(23*num)%256,255),2)
        return image

    # detection and send message   
    def work(self, v_id, v_type, video_id=0, l = 0 , r = 0, t= 0, b = 0):
        global detection_graph, close_thread, cam, sess, show_id
        with detection_graph.as_default():
            camera = cv2.VideoCapture(v_id)
            img = None
            count = 1
            while camera.isOpened():
                ret, frame = camera.read() 
                if ret:
                    image = frame
                    image_data = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image_data_expanded = np.expand_dims(image_data, axis=0)
                    if count % 5 == 0:
                        count = 0
                        image, img, name = self.object_detection(image, image_data_expanded, sess)
                        image = self.tracking(img, image, name)
                        h, w, _ = image.shape
                        if v_type != 0:
                            for i in range(len(img)):
                                ymin, xmin, ymax, xmax = self.out_boxes[i]
                                left, right, top, bottom = (xmin * w, xmax * w,
                                                          ymin * h, ymax * h)
                                top = max(0, np.floor(top + 0.5).astype('int32'))
                                left = max(0, np.floor(left + 0.5).astype('int32'))
                                bottom = min(h, np.floor(bottom + 0.5).astype('int32'))
                                right = min(w, np.floor(right + 0.5).astype('int32'))  
                                center = [(top+bottom)/2.0, (left+right)/2.0]
                                judge_alarm(l, r, t, b, center, video_id, name[i])
                    else:
                        image, img, name = draw_boxes(image, self.out_scores, self.out_boxes, self.out_classes, self.class_names, self.colors)
                        image = self.tracking(img, image, name)
                    if show_id == 0 or len(self.tracking_save) == 0:
                        yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + self.trans(image) + b'\r\n\r\n')
                    else:
                        if len(self.tracking_save) > 0:
                            yield (b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + self.trans(self.tracking_save[0]) + b'\r\n\r\n')                    
                count += 1
                if close_thread != 0:
                    break
            camera.release()
            cv2.destroyAllWindows()
