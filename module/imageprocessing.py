import cv2                   # OpenCV
import numpy as np           # Create arrays
from threading import Thread, Lock # Multithreading & Lock
import time                  # Mesure FPS

from module.threadedcamera import ThreadedCamera

# OpenCV2: Process picture
# Resize img
def Resize_img(img, x, y, gpu=False):
    if gpu: # gpu
        return cv2.cuda.resize(img,(x, y),interpolation=cv2.INTER_LINEAR) # Resize image
    else: # cpu
        return cv2.resize(img,(x, y),interpolation=cv2.INTER_LINEAR) # Resize image

# Undistort img
def Calculate_Undistort(img, number_of_calibration_points_per_line, calibration_points):
    # cordinates of the calibration points
    objp = np.zeros((int(number_of_calibration_points_per_line*number_of_calibration_points_per_line),3), np.float32)
    objp[:,:2] = np.mgrid[0:number_of_calibration_points_per_line,0:number_of_calibration_points_per_line].T.reshape(-1,2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # list of found objects
    objpoints = []
    imgpoints = []


    objpoints.append(objp)
    imgpoints.append(np.array(calibration_points).astype(np.float32)) 

    # Calculate intrinsic and extrinsic parameters of the camera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    return mtx, dist, newcameramtx


def Undistort_img(img, mtx, dist, newcameramtx, gpu=False):
        if gpu:
            return img
        else:
            # Remove distortion from the image
            return cv2.undistort(img, mtx, dist, None, newcameramtx)
        
# Warp img
def Warp_img(img, corners, scale_x, scale_y, border_buffer, gpu=False):
    pts1 = np.float32(corners)
    pts2 = np.float32([[0,0],[scale_x+border_buffer*2,0],[0,scale_y+border_buffer*2],[scale_x+border_buffer*2,scale_y+border_buffer*2]])
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    if gpu: # gpu
        return cv2.cuda.warpPerspective(img,matrix,(scale_x+border_buffer*2,scale_y+border_buffer*2))
    else: # cpu
        return cv2.warpPerspective(img,matrix,(scale_x+border_buffer*2,scale_y+border_buffer*2))
 
# HSV mask
def HSV_img(img, gpu=False):
    if gpu:
        return cv2.cuda.cvtColor(img,cv2.COLOR_BGR2HSV)
    else:
        return cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

# Mask1
def Mask_img(img, lower, upper, gpu=False):
    if gpu:
        return cv2.cuda.inRange(img, lower, upper)
    else:
        return cv2.inRange(img, lower, upper)
    

# Blur img
def Blur_img(img, blur, gpu=False):
    if blur == 0:
        return img
    if gpu:
        return img # todo blur gpu support
    else:
        return cv2.blur(img, (blur,blur), cv2.BORDER_DEFAULT)

# Detect blobs
def Detect_blob(img, border_buffer, detector=None, minArea=50, calibration_status=0, gpu=False):
    if gpu:
        hcd = cv2.cuda.createHoughCirclesDetector(1, 100, 120, 10, 5, 100, 1)
        coordinates = hcd.detect(img)
        
        coordinates = coordinates.download()
        if coordinates is not None:
            coordinates = coordinates[0]
        else:
            coordinates = ()
        
        keypoints = ()
    else:
        if detector is None:
            params = cv2.SimpleBlobDetector_Params()
            params.filterByArea = True
            params.minArea = minArea
            detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(img) # keypoints
        coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
        
    if len(coordinates) > 0 and calibration_status == 0:
        for c in coordinates:
            c[0] = c[0] - (border_buffer * 2)
            c[1] = c[1] - (border_buffer * 2)
    return coordinates, keypoints

# Write blob coordinates to img
def Draw_coordinates(img, orgx, orgy, text, color=(255, 255, 255)):
    return cv2.putText(img, text, (orgx+25,orgy-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

# Write blob coordinates to img
def Draw_blobsize(img, orgx, orgy, text, color=(255, 255, 255)):
    return cv2.putText(img, text, (orgx+25,orgy+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

# Draw circle around blob
Blank = np.zeros((1, 1))
def Draw_blobs(img, keypoints, color=(255, 255, 255)):
    return cv2.drawKeypoints(img, keypoints, Blank, color,cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Write FPS to img
prev_frame_time = 0
new_frame_time = 0
def Write_Text(img, text):
    cv2.putText(img, text, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 255, 0), 3, cv2.LINE_AA)

# 4 pictures to 1 img
def Stack_img(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

# Draw Point
def Draw_point(img, coordinates, radius=10, color=(136, 0, 21)):
    return cv2.circle(img, (int(coordinates[0]), int(coordinates[1])), radius=radius, color=color, thickness=-1)


class ImageProcessing():
    threads = []
    
    def __init__(self, conf, threads = 1):
        self.Conf = conf
        # Set camera input
        self.cap = ThreadedCamera(self.Conf.CAMERA_X, self.Conf.CAMERA_Y, self.Conf.CAMERA_FPS, self.Conf.CAMERA_SRC, self.Conf.CV2_ALGORITHM_NUMBER)
        
        for n in range(threads):
            # Start frame retrieval thread
            self.threads.append(self.ThreadObject(n, self.Conf, self.cap))


    class ThreadObject():
        def __init__(self, number, conf, cap):
            self.number = number
            self.Conf = conf
            self.cap = cap
            self.lock = Lock()
            self.status = False
            self.Running = True
            self.debug_img = None
            self.coordinates = []
            self.blobSizes = []
            self.prev_frame_time = time.time()
            self.new_frame_time = time.time()

            # Cache blob detector
            params = cv2.SimpleBlobDetector_Params()
            params.filterByArea = True
            params.minArea = 50
            self.detector = cv2.SimpleBlobDetector_create(params)

            self.thread = Thread(target=self.Run, args=())
            self.thread.daemon = True
            self.thread.start()
            
        def getFPS(self):
            self.new_frame_time = time.time()
            diff = self.new_frame_time - self.prev_frame_time
            fps = 1 / diff if diff > 0 else 0
            self.prev_frame_time = self.new_frame_time
            return int(fps)
            
        def Run(self):
            while self.Running:
                img, captureFps = self.cap.grap_frame() # Read img
                if img is None:
                    time.sleep(0.005)
                    continue
                
                gpu = self.Conf.GPU_ENABLED

                if gpu:
                    img = cv2.cuda_GpuMat(img)  # Upload img to GPU

                img = Resize_img(img, self.Conf.SCALE_X, self.Conf.SCALE_Y, gpu) # Resize image

                # Warp image
                if self.Conf.Calibrate_Status == 0:
                    number_of_points = self.Conf.NUMBER_OF_CALIBRATION_POINTS_PER_LINE * self.Conf.NUMBER_OF_CALIBRATION_POINTS_PER_LINE
                    corners = [
                        self.Conf.CALIBRATION_POINTS[0].copy(),                                                                     # Top left
                        self.Conf.CALIBRATION_POINTS[number_of_points - self.Conf.NUMBER_OF_CALIBRATION_POINTS_PER_LINE].copy(),    # Top right
                        self.Conf.CALIBRATION_POINTS[self.Conf.NUMBER_OF_CALIBRATION_POINTS_PER_LINE - 1].copy(),                   # Bottom left
                        self.Conf.CALIBRATION_POINTS[number_of_points-1].copy()                                                     # Bottom right
                    ]
                    # top left
                    corners[0][1] = corners[0][1] + self.Conf.BORDER_BUFFER
                    corners[0][0] = corners[0][0] - self.Conf.BORDER_BUFFER
                    # top right
                    corners[1][0] = corners[1][0] - self.Conf.BORDER_BUFFER
                    corners[1][1] = corners[1][1] - self.Conf.BORDER_BUFFER
                    # bottom left
                    corners[2][0] = corners[2][0] + self.Conf.BORDER_BUFFER
                    corners[2][1] = corners[2][1] + self.Conf.BORDER_BUFFER
                    # bottom right
                    corners[3][0] = corners[3][0] - self.Conf.BORDER_BUFFER
                    corners[3][1] = corners[3][1] + self.Conf.BORDER_BUFFER

                    img = Warp_img(img, corners, self.Conf.SCALE_X, self.Conf.SCALE_Y, self.Conf.BORDER_BUFFER, gpu)

                # HSV mask
                imgHSV = HSV_img(img, gpu)
                mask = Mask_img(imgHSV, self.Conf.MASK_LOWER, self.Conf.MASK_UPPER, gpu)
                
                # Blur image
                blur = Blur_img(mask, self.Conf.BLUR, gpu)

                # Detect blobs using cached detector
                coordinates, keypoints = Detect_blob(blur, self.Conf.BORDER_BUFFER, detector=self.detector, minArea=50, calibration_status=self.Conf.Calibrate_Status, gpu=gpu)
                
                # If no blob detected and debug is false, continue
                if len(coordinates) == 0 and not self.Conf.DEBUG:
                    continue
                
                # Get blob size
                blobSizes = []
                for k in keypoints:
                    blobSizes.append(k.size)
                
                if len(keypoints) == 0:
                    for _ in coordinates:
                        blobSizes.append(50)
                
                debug_img = None
                if self.Conf.DEBUG: # Draw keypoints in image
                    if gpu:
                        img = img.download()
                        imgHSV = imgHSV.download()
                        mask = mask.download()
                        blur = blur.download()
                    
                    count = 0
                    for p in coordinates:
                        orgx = int(p[0])
                        orgy = int(p[1])
                        realX = int(orgx * self.Conf.SCALE_FACTOR_X)
                        realY = int(orgy * self.Conf.SCALE_FACTOR_Y)
                        text = f"{realX}|{realY}"
                        img = Draw_coordinates(img, orgx, orgy, text, (255, 255, 255))
                        textblobsize = str(round(blobSizes[count], 2)) if count < len(blobSizes) else "50"
                        img = Draw_blobsize(img, orgx, orgy, textblobsize, (255, 255, 255))
                        count += 1
                    
                    img = Draw_blobs(img, keypoints, (255, 255, 255))
                    if len(coordinates) > 0:
                        point = coordinates[0]
                        img = Draw_point(img, point, 10, (136, 0, 21))

                    # Draw all calibration points
                    if self.Conf.Calibrate_Status > 0 and not gpu:
                        for point in self.Conf.CALIBRATION_POINTS:
                            img = Draw_point(img, point, 10, (0, 0, 255))

                    # show fps
                    fps = self.getFPS()
                    fpstext = f"FPS: {fps}"
                    Write_Text(mask, fpstext)
                    cap_fps_val = int(captureFps) if captureFps else 0
                    capturetext = f"Capture: {cap_fps_val}"
                    Write_Text(img, capturetext)
                    gputext = "GPU: Enabled" if gpu else "GPU: Disabled"
                    Write_Text(blur, gputext)

                    try:
                        debug_img = Stack_img(0.5, ([img, imgHSV], [mask, blur]))
                    except Exception:
                        debug_img = None

                with self.lock:
                    self.coordinates = coordinates
                    self.blobSizes = blobSizes
                    self.debug_img = debug_img
                    self.status = True
        
        def end(self):
            self.Running = False
            with self.lock:
                self.status = False

            
    def grap_coordinates(self):
        for th in self.threads:
            with th.lock:
                if th.status:
                    th.status = False
                    return True, th.debug_img, list(th.coordinates), list(th.blobSizes)
        return False, None, None, None
    
    def end(self):
        for th in self.threads:
            th.end()
        self.threads = []
        if hasattr(self, 'cap'):
            self.cap.end()