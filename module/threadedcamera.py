import cv2                   # OpenCV
from threading import Thread, Lock # Multithreading & synchronization
import time                  # Measure FPS
import sys

# Relevant video capture backends for Linux / Cross-platform
cv2_algorithms = (
    (cv2.CAP_ANY, "CAP_ANY"),                   # Auto detect
    (cv2.CAP_V4L2, "CAP_V4L2"),                 # V4L2 capturing (standard on Linux)
    (cv2.CAP_GSTREAMER, "CAP_GSTREAMER"),       # GStreamer
    (cv2.CAP_FFMPEG, "CAP_FFMPEG"),             # FFMPEG
)

def test_algorithm(algo, test_time=0.5, src=0):
    cap = ThreadedCamera(720, 576, fps=30, src=src, algorithm=algo[0])
    if not cap.Status():
        return (algo[0], algo[1], -1)
    average = 0
    counter = 0
    start = time.time()
    while time.time() - start < test_time:
        img, fps = cap.grap_frame()
        if img is None:
            time.sleep(0.01)
            continue
        if fps:
            average += fps
            counter += 1
        time.sleep(0.005)
        
    cap.end()
    avg_fps = (average / counter) if counter > 0 else 0
    print(f"Average FPS for algorithm {algo[1]}: {avg_fps:.1f}")
    return (algo[0], algo[1], avg_fps)

def find_cv2_algorithm(test_time=0.5, src=0):
    results = []
    for algo in cv2_algorithms:
        try:
            res = test_algorithm(algo, test_time, src=src)
            if res[2] > 0:
                results.append(res)
        except Exception:
            continue
    if not results:
        return [(cv2.CAP_ANY, "CAP_ANY", 30.0)]
    results = sorted(results, key=lambda x: float(x[2]), reverse=True)
    return results

def find_camera():
    index = 0
    arr = []
    while index < 10:  # Check up to 10 video devices
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            break
        ret, _ = cap.read()
        if ret:
            arr.append(index)
        cap.release()
        index += 1
    return arr

# Capture picture parallel
class ThreadedCamera(object):    
    def __init__(self, Cam_X, Cam_Y, fps, src=0, algorithm=cv2.CAP_ANY):
        self.lock = Lock()
        self.Running = False
        self.status = False
        self.frame = None
        self.fps = 0
        self.capture = None
        self.start(Cam_X, Cam_Y, fps, src, algorithm)
        
    def Status(self):
        return self.Running

    def start(self, Cam_X, Cam_Y, fps, src=0, algorithm=cv2.CAP_ANY):
        if src is None:
            src = 0
        try:
            self.capture = cv2.VideoCapture(src, algorithm)
            if self.capture is None or not self.capture.isOpened():
                print(f"Camera source {src} or algorithm {algorithm} is invalid")
                self.Running = False
                return
        except Exception as e:
            print(f"Failed to open camera: {e}")
            self.Running = False
            return
        
        print("apiPreference (cv2 Backend):", self.capture.getBackendName())
        
        cv2.useOptimized()
        # Set img size of camera (x,y)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, Cam_X)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, Cam_Y)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture.set(cv2.CAP_PROP_FPS, fps)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        self.lastTime = time.time()
        self.Running = True
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def end(self):
        self.Running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.capture and self.capture.isOpened():
            self.capture.release()
        
    def update(self):
        while self.Running:
            if self.capture and self.capture.isOpened():
                newTime = time.time()
                diff = newTime - self.lastTime
                if diff <= 0:
                    diff = 1e-4
                calculated_fps = 1.0 / diff
                self.lastTime = newTime
                ret, frame = self.capture.read()
                with self.lock:
                    self.status = ret
                    self.frame = frame
                    self.fps = calculated_fps
            else:
                time.sleep(0.01)
    
    def grap_frame(self):
        with self.lock:
            if self.status and self.frame is not None:
                return self.frame.copy(), self.fps
            return None, None