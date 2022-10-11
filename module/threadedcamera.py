import cv2                   # OpenCV
from threading import Thread # Multitreading
import time                  # Mesure FPS

# Capture picture parallel
class ThreadedCamera(object):
    def __init__(self, Cam_X, Cam_Y, src=0):
        self.capture = cv2.VideoCapture(src)        
        cv2.useOptimized()
        # Set img size of camera (x,y)
        self.capture.set(3, Cam_X)
        self.capture.set(4, Cam_Y)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.lastTime = time.time() 
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
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
        
    def end(self):
        self.capture.release()