import cv2                   # OpenCV
import numpy as np           # Create arrays
from threading import Thread # Multitreading
import time                  # Mesure FPS

from module.threadedcamera import ThreadedCamera

# OpenCV2: Process picture
# Resize img
def Resize_img(img, x, y, gpu=False):
    if gpu: # gpu
        return cv2.cuda.resize(img,(x, y),interpolation=cv2.INTER_LINEAR) # Resize image
    else: # cpu
        return cv2.resize(img,(x, y),interpolation=cv2.INTER_LINEAR) # Resize image

# Warp img
def Warp_img(img, corners, scale_x, scale_y, boarder_buffer, gpu=False):
    pts1 = np.float32(corners)
    pts2 = np.float32([[0,0],[scale_x+boarder_buffer*2,0],[0,scale_y+boarder_buffer*2],[scale_x+boarder_buffer*2,scale_y+boarder_buffer*2]])
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    if gpu: # gpu
        return cv2.cuda.warpPerspective(img,matrix,(scale_x+boarder_buffer*2,scale_y+boarder_buffer*2))
    else: # cpu
        return cv2.warpPerspective(img,matrix,(scale_x+boarder_buffer*2,scale_y+boarder_buffer*2))
 
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
        # return cv2.cuda.blur(img, (blur,blur), cv2.BORDER_DEFAULT)
        return img # todo blur gpu support
    else:
        return cv2.blur(img, (blur,blur), cv2.BORDER_DEFAULT)

# Detect blobs
def Detect_blob(img, minArea = 100, gpu=False):
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
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = minArea
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(img) # keypoints
        coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
    return coordinates, keypoints

# Write blob coordinates to img
def Draw_coordinates(img, orgx, orgy, text, color=(255, 255, 255)):
    return cv2.putText(img, text, (orgx+25,orgy-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

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
            self.thread = Thread(target=self.Run, args=())
            self.thread.daemon = True
            self.thread.start()
            
        prev_frame_time = 0
        new_frame_time = 0
        def getFPS(self):
            self.new_frame_time = time.time()
            fps = 1/(self.new_frame_time-self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
            return int(fps)
            
        Running = True
        def Run(self):
            while self.Running:
                # try:
                img, captureFps = self.cap.grap_frame() # Read img
                if img is None:
                    continue
                
                gpu = self.Conf.GPU_ENABLED

                if gpu:
                    img = cv2.cuda_GpuMat(img)  # Uploade img to GPU

                img = Resize_img(img, self.Conf.SCALE_X, self.Conf.SCALE_Y, gpu) # Resize image

                #Warp image
                if self.Conf.Calibrate_Status == 0:
                    img = Warp_img(img, self.Conf.CORNERS, self.Conf.SCALE_X, self.Conf.SCALE_Y, self.Conf.BORDER_BUFFER, gpu)

                #HSV mask
                imgHSV = HSV_img(img, gpu)
                mask = Mask_img(imgHSV, self.Conf.MASK_LOWER, self.Conf.MASK_UPPER, gpu)
                
                #Blur image
                blur = Blur_img(mask, self.Conf.BLUR, gpu)

                #Detect blobs.
                self.coordinates, keypoints = Detect_blob(blur, 50, gpu)
                
                # print(self.coordinates)
                # print(keypoints)
                
                # If no blob detected continue
                if len(self.coordinates) == 0 and self.Conf.DEBUG == False:
                    continue
                
                # Get blob size
                self.blobSizes = []
                for k in keypoints:
                    self.blobSizes.append(k.size)
                
                if len(keypoints) == 0:
                    for c in self.coordinates:
                        self.blobSizes.append(50)
                
                
                if self.Conf.DEBUG == True: # Draw the keypoints in image
                    if gpu:
                        img = img.download()
                        imgHSV = imgHSV.download()
                        mask = mask.download()
                        blur = blur.download()
                    
                    for p in self.coordinates:
                        orgx = int(p[0])
                        orgy = int(p[1])
                        newx = self.Conf.SCALE_X-orgx+self.Conf.BORDER_BUFFER-1
                        newy = orgy-self.Conf.BORDER_BUFFER
                        realX = int(newx*self.Conf.SCALE_FACTOR_X)
                        realY = int(newy*self.Conf.SCALE_FACTOR_Y)
                        text = str(realX) + "|" + str(realY)
                        img = Draw_coordinates(img, orgx, orgy, text, (255, 255, 255))
                    
                    img = Draw_blobs(img, keypoints, (255, 255, 255))
                    
                    # show fps
                    fps = self.getFPS()
                    fpstext = "FPS: " + str(fps)
                    Write_Text(mask, fpstext)
                    capturetext = "Capture: " + str(int(captureFps))
                    Write_Text(img, capturetext)
                    if gpu == True:
                        gputext = "GPU: Enabled"
                    else:
                        gputext = "GPU: Disabled"
                    Write_Text(blur, gputext)

                    # If debug mode is enabled, print image
                    try:
                        self.debug_img = Stack_img(0.5,([img,imgHSV],[mask,blur]))
                    except:
                        self.debug_img = None
                else:
                    self.debug_img = None
        
                # set status to 1 -> img processing done
                self.status = True
                # except:
                #     self.status = False
        
        # def grap_coordinates(self):
        #     try:
        #         if self.status:
        #             return True, self.debug_img, self.coordinates, self.keypoints
        #         return False, None, None, None
        #     except:
        #         return False, None, None, None
        
        def end(self):
            self.Running = False
            self.status = False

            
    def grap_coordinates(self):
        for th in self.threads:
            try:
                if th.status:
                    th.status = False
                    return True, th.debug_img, th.coordinates, th.blobSizes # Todo: Blob direction and time
            except:
                continue
        return False, None, None, None
    
    def end(self):
        for th in self.threads:
            th.end()
        self.threads = []