import cv2                   # OpenCV
from threading import Thread # Multitreading
import time                  # Mesure FPS
import sys

cv2_algorithms = (
    (cv2.CAP_ANY, "CAP_ANY"),                   # Auto detect == 0
    (cv2.CAP_VFW, "CAP_VFW"),                   # Video For Windows (platform native)
    (cv2.CAP_V4L, "CAP_V4L"),                   # V4L/V4L2 capturing support via libv4l
    (cv2.CAP_V4L2, "CAP_V4L2"),                 # Same as CAP_V4L
    (cv2.CAP_FIREWIRE, "CAP_FIREWIRE"),         # IEEE 1394 drivers
    (cv2.CAP_FIREWARE, "CAP_FIREWARE"),         # Same as CAP_FIREWIRE
    (cv2.CAP_IEEE1394, "CAP_ANY"),              # Same as CAP_FIREWIRE
    (cv2.CAP_DC1394, "CAP_ANY"),                # Same as CAP_FIREWIRE
    (cv2.CAP_CMU1394, "CAP_CMU1394"),           # Same as CAP_FIREWIRE
    (cv2.CAP_QT, "CAP_QT"),                     # QuickTime
    (cv2.CAP_UNICAP, "CAP_UNICAP"),             # Unicap drivers
    (cv2.CAP_DSHOW, "CAP_DSHOW"),               # DirectShow (via videoInput) 
    (cv2.CAP_PVAPI, "CAP_PVAPI"),               # PvAPI, Prosilica GigE SDK
    (cv2.CAP_OPENNI, "CAP_OPENNI"),             # OpenNI (for Kinect) 
    (cv2.CAP_OPENNI_ASUS, "CAP_OPENNI_ASUS"),   # OpenNI (for Asus Xtion) 
    (cv2.CAP_ANDROID, "CAP_ANDROID"),           # Android - not used. 
    (cv2.CAP_XIAPI, "CAP_XIAPI"),               # XIMEA Camera API
    (cv2.CAP_AVFOUNDATION, "CAP_AVFOUNDATION"), # AVFoundation framework for iOS (OS X Lion will have the same API)
    (cv2.CAP_GIGANETIX, "CAP_GIGANETIX"),       # Smartek Giganetix GigEVisionSDK.
    (cv2.CAP_MSMF, "CAP_MSMF"),                 # Microsoft Media Foundation (via videoInput) 
    (cv2.CAP_WINRT, "CAP_WINRT"),               # Microsoft Windows Runtime using Media Foundation. 
    (cv2.CAP_INTELPERC, "CAP_INTELPERC"),       # Intel Perceptual Computing SDK. 
    (cv2.CAP_OPENNI2, "CAP_OPENNI2"),           # OpenNI2 (for Kinect) 
    (cv2.CAP_OPENNI2_ASUS, "CAP_OPENNI2_ASUS"), # OpenNI2 (for Asus Xtion and Occipital Structure sensors
    (cv2.CAP_GPHOTO2, "CAP_GPHOTO2"),           # gPhoto2 connection 
    (cv2.CAP_GSTREAMER, "CAP_GSTREAMER"),       # GStreamer. 
    (cv2.CAP_FFMPEG, "CAP_FFMPEG"),             # Open and record video file or stream using the FFMPEG library.
    (cv2.CAP_IMAGES, "CAP_IMAGES"),             # OpenCV Image Sequence (e.g. img_%02d.jpg) 
    (cv2.CAP_ARAVIS, "CAP_ARAVIS"),             # Aravis SDK. 
    (cv2.CAP_OPENCV_MJPEG, "CAP_OPENCV_MJPEG"), # Built-in OpenCV MotionJPEG codec.
    (cv2.CAP_INTEL_MFX, "CAP_CAP_INTEL_MFXNY"), # Intel MediaSDK. 
    (cv2.CAP_XINE, "CAP_XINE")                   # XINE engine (Linux) 
)

def test_algorithm(algo, test_time):
    cap = ThreadedCamera(720, 576, 0, algo[0])
    if not cap.Status():
        return (algo[0], algo[1], -1)
    average = 0
    counter = 1
    start = time.time()
    run = True
    while run:
        if time.time() - start > test_time:
            print("Average FPS for algorithm {}: {}".format(algo[1], average/counter))
            run = False
            break
        
        img, fps = cap.grap_frame()
        if img is None:
            continue
        average += fps
        counter += 1
        
    cap.end()
    return (algo[0], algo[1], (average / counter))

def find_cv2_algorithm(test_time = 5):
    list = []
    for algo in cv2_algorithms:
        list.append(test_algorithm(algo, test_time))
    list = sorted(list, key = lambda x: float(x[2]), reverse=True)
    # print(list)
    return list

def find_camera():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

# Capture picture parallel
class ThreadedCamera(object):    
    def __init__(self, Cam_X, Cam_Y, src=0, algorithm=cv2.CAP_ANY):
        self.start(Cam_X, Cam_Y, src, algorithm)
        
    def Status(self):
        return self.Running

    def start(self, Cam_X, Cam_Y, src=None, algorithm=cv2.CAP_ANY):
        try:
            self.capture = cv2.VideoCapture(src, algorithm)
            # Test camera inpur src
            if self.capture is None or not self.capture.isOpened():
                print("Camera src or algorythem is wrong")
                self.Running = False
                return
        except:
            print("Camera src or algorythem is wrong")
            self.Running = False
            return
        
        print("apiPreference (cv2 Backend): ", self.capture.getBackendName())
        
        cv2.useOptimized()
        # Set img size of camera (x,y)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, Cam_X)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, Cam_Y)
        self.capture.set(cv2.CAP_PROP_FPS, 30);
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        self.lastTime = time.time() 
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def end(self):
        self.Running = False
        self.capture.release()
        
        
    Running = True
    def update(self):
        while self.Running:
            if self.capture.isOpened():
                newTime = time.time()
                diff = newTime - self.lastTime
                if diff == 0: # Prevent division by zero
                    diff = 1
                self.fps = 1 / diff
                self.lastTime = newTime
                (self.status, self.frame) = self.capture.read()
    
    def grap_frame(self):
        try:
            if self.status:
                return self.frame, self.fps
            return None, None
        except:
            return None, None