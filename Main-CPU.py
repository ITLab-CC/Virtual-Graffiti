from ast import Try
import cv2
import numpy as np
import json
from os.path import exists
import mss
#from pymouse import PyMouse

#mouse = PyMouse()
import mouse

class Config:
    DEBUG = True
    CONFIG_FILE="config.conf"
    SCREEN_X=1920
    SCREEN_Y=1080
    CAMERA_X=1920
    CAMERA_Y=1080
    try:
        sct=mss.mss()
        SCREEN_X=int(sct.monitors[1]['width'])
        SCREEN_Y=int(sct.monitors[1]['height'])
    except:
        SCREEN_X=1920
        SCREEN_Y=1080
    SCALE_X=int(SCREEN_X/2)
    SCALE_Y=int(SCREEN_Y/2)
    SCALE_FACTOR_X = SCREEN_X/SCALE_X
    SCALE_FACTOR_Y = SCREEN_Y/SCALE_Y
    CORNERS=[[77, 7], [897, 25], [81, 501], [870, 517]]
    MASK_COLORS=[0, 179, 0, 255, 0, 145]
    BLUR = 1
    BORDER_BUFFER=20
    
    # def __init__(self):
    #     self.LoadFromJSON()
            
    def copy(self, other=None):
        if not(isinstance(other,Config)) or other==None:
            other = Config()
        else:
            other = self
        other.CORNERS=self.CORNERS.copy()
        other.MASK_COLORS=self.MASK_COLORS.copy()
        return other

    #Save vars to config.conf file
    def SaveToJSON(self):
        data = {
            'config' : {
                'DEBUG': self.DEBUG,
                'SCREEN_X' : self.SCREEN_X,
                'SCREEN_Y' : self.SCREEN_Y,
                'CAMERA_X' : self.CAMERA_X,
                'CAMERA_Y' : self.CAMERA_Y,
                'SCALE_X' : self.SCALE_X,
                'SCALE_Y' : self.SCALE_Y,
                'CORNERS' : self.CORNERS,
                'MASK_COLORS' : self.MASK_COLORS,
                'BLUR' : self.BLUR,
                'BORDER_BUFFER' : self.BORDER_BUFFER
            }
        }
        with open(self.CONFIG_FILE, 'w') as outfile:
            json.dump(data, outfile)

    #Load vars from config.conf file
    def LoadFromJSON(self):
        if not exists(self.CONFIG_FILE):
            self.SaveToJSON()
            return
        try:
            with open(self.CONFIG_FILE) as json_file:
                data = json.load(json_file)
                self.DEBUG = data['config']['DEBUG']
                if self.DEBUG == "true":
                    self.DEBUG = True
                if self.DEBUG == "false":
                    self.DEBUG = False
                self.SCREEN_X = data['config']['SCREEN_X']
                self.SCREEN_Y = data['config']['SCREEN_Y']
                self.CAMERA_X = data['config']['CAMERA_X']
                self.CAMERA_Y = data['config']['CAMERA_Y']
                self.SCALE_X = data['config']['SCALE_X']
                self.SCALE_Y = data['config']['SCALE_Y']
                self.CORNERS = data['config']['CORNERS']
                self.MASK_COLORS = data['config']['MASK_COLORS']
                self.BLUR = data['config']['BLUR']
                self.BORDER_BUFFER = data['config']['BORDER_BUFFER']
                self.SCALE_FACTOR_X = self.SCREEN_X/self.SCALE_X
                self.SCALE_FACTOR_Y = self.SCREEN_Y/self.SCALE_Y
        except:
            print("The config has a wrong format. Delete the file and a new one will be generated")    



#Options menu
def setTrackbarPos():
    try:
        CONF.SCALE_X = cv2.getTrackbarPos("Scale X","Options")
        CONF.SCALE_Y = cv2.getTrackbarPos("Scale Y","Options")
        CONF.MASK_COLORS[0] = cv2.getTrackbarPos("Hue Min","Options")
        CONF.MASK_COLORS[1] = cv2.getTrackbarPos("Hue Max","Options")
        CONF.MASK_COLORS[2] = cv2.getTrackbarPos("Sat Min","Options")
        CONF.MASK_COLORS[3] = cv2.getTrackbarPos("Sat Max","Options")
        CONF.MASK_COLORS[4] = cv2.getTrackbarPos("Val Min","Options")
        CONF.MASK_COLORS[5] = cv2.getTrackbarPos("Val Max","Options")
        CONF.BLUR = cv2.getTrackbarPos("Blur","Options")
        CONF.BORDER_BUFFER = cv2.getTrackbarPos("Boarder Buffer","Options")
        if CONF.BLUR < 1:
            cv2.setTrackbarPos("Blur","Options", 1)
            CONF.BLUR = 1
        if CONF.SCALE_X < 1:
            cv2.setTrackbarPos("Scale X","Options", 1)
            CONF.SCALE_X = 1
        if CONF.SCALE_Y < 1:
            cv2.setTrackbarPos("Scale Y","Options", 1)
            CONF.SCALE_Y = 1
        CONF.SaveToJSON()
        CONF.SCALE_FACTOR_X = CONF.SCREEN_X/CONF.SCALE_X
        CONF.SCALE_FACTOR_Y = CONF.SCREEN_Y/CONF.SCALE_Y
    except:
        return;

def Button_Reset():
    global CONF
    global CONF_OLD
    CONF = CONF_OLD.copy() # Restore conf
    cv2.setTrackbarPos("Scale X","Options", CONF.SCALE_X)
    cv2.setTrackbarPos("Scale Y","Options", CONF.SCALE_Y)
    cv2.setTrackbarPos("Hue Min","Options", CONF.MASK_COLORS[0])
    cv2.setTrackbarPos("Hue Max","Options", CONF.MASK_COLORS[1])
    cv2.setTrackbarPos("Sat Min","Options", CONF.MASK_COLORS[2])
    cv2.setTrackbarPos("Sat Max","Options", CONF.MASK_COLORS[3])
    cv2.setTrackbarPos("Val Min","Options", CONF.MASK_COLORS[4])
    cv2.setTrackbarPos("Val Max","Options", CONF.MASK_COLORS[5])
    cv2.setTrackbarPos("Blur","Options", CONF.BLUR)
    cv2.setTrackbarPos("Boarder Buffer", CONF.BORDER_BUFFER)
    cv2.setTrackbarPos("Reset","Options", 0)
    print("Reseted to: ", CONF.MASK_COLORS[0], CONF.MASK_COLORS[1], CONF.MASK_COLORS[2], CONF.MASK_COLORS[3], CONF.MASK_COLORS[4], CONF.MASK_COLORS[5], CONF.BLUR)

# Open/Create options menu
global Option_Menu_Open
Option_Menu_Open = False
def Option_Colo_Open():
    if cv2.getWindowProperty("Options",cv2.WND_PROP_VISIBLE) <= 0:
        global Option_Menu_Open
        Option_Menu_Open = True
        global CONF
        global CONF_OLD
        CONF_OLD = CONF.copy() # Backup conf
        cv2.namedWindow("Options")
        cv2.resizeWindow("Options",300,600)
        cv2.createTrackbar("Scale X","Options",CONF.SCALE_X,CONF.CAMERA_X, setTrackbarPos)
        cv2.createTrackbar("Scale Y","Options",CONF.SCALE_Y,CONF.CAMERA_Y, setTrackbarPos)
        cv2.createTrackbar("Hue Min","Options",CONF.MASK_COLORS[0],255, setTrackbarPos)
        cv2.createTrackbar("Hue Max","Options",CONF.MASK_COLORS[1],255, setTrackbarPos)
        cv2.createTrackbar("Sat Min","Options",CONF.MASK_COLORS[2],255, setTrackbarPos)
        cv2.createTrackbar("Sat Max","Options",CONF.MASK_COLORS[3],255, setTrackbarPos)
        cv2.createTrackbar("Val Min","Options",CONF.MASK_COLORS[4],255, setTrackbarPos)
        cv2.createTrackbar("Val Max","Options",CONF.MASK_COLORS[5],255, setTrackbarPos)
        cv2.createTrackbar("Blur","Options",CONF.BLUR,20, setTrackbarPos)
        cv2.createTrackbar("Boarder Buffer","Options", CONF.BORDER_BUFFER,50, setTrackbarPos)
        cv2.createTrackbar("Reset","Options",0,1, Button_Reset)



#Calibration mode
global Calibrate_Status
Calibrate_Status = 0
def Calibrate_Points(x=-1, y=-1):
    global Calibrate_Status
    global CONF
    if x < 0:
        x = CONF.SCREEN_X
    if y < 0:
        y = CONF.SCREEN_Y

    cal_imag = np.zeros((CONF.SCREEN_Y,CONF.SCREEN_X,3), np.uint8)

    if Calibrate_Status == 1:
        cv2.circle(cal_imag,(0,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,15), 15, (255,0,0), -1)
        if((x > int(CONF.SCALE_X/2)) and (y < int(CONF.SCALE_Y/2))):
            CONF.CORNERS[1][0] = x+CONF.BORDER_BUFFER
            CONF.CORNERS[1][1] = y-CONF.BORDER_BUFFER
            Calibrate_Status = 2
    elif Calibrate_Status == 2:
        cv2.circle(cal_imag,(CONF.SCREEN_X-1,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(CONF.SCREEN_X-16,15), 15, (255,0,0), -1)
        if((x < int(CONF.SCALE_X/2)) and (y < int(CONF.SCALE_Y/2))):
            CONF.CORNERS[0][0] = x-CONF.BORDER_BUFFER
            CONF.CORNERS[0][1] = y-CONF.BORDER_BUFFER
            Calibrate_Status = 3
    elif Calibrate_Status == 3:
        cv2.circle(cal_imag,(0,CONF.SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,CONF.SCREEN_Y-16), 15, (255,0,0), -1)
        if((x > int(CONF.SCALE_X/2)) and (y > int(CONF.SCALE_Y/2))):
            CONF.CORNERS[3][0] = x+CONF.BORDER_BUFFER
            CONF.CORNERS[3][1] = y+CONF.BORDER_BUFFER
            Calibrate_Status = 4
    elif Calibrate_Status == 4:
        cv2.circle(cal_imag,(CONF.SCREEN_X-1,CONF.SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(CONF.SCREEN_X-16,CONF.SCREEN_Y-16), 15, (255,0,0), -1)
        if((x < int(CONF.SCALE_X/2)) and (y > int(CONF.SCALE_Y/2))):
            CONF.CORNERS[2][0] = x-CONF.BORDER_BUFFER
            CONF.CORNERS[2][1] = y+CONF.BORDER_BUFFER
            Calibrate_Status = 0

    cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Calibrate", cal_imag)
    if Calibrate_Status == 0:
        CONF.SaveToJSON()
        cv2.destroyWindow("Calibrate")  
            



#Switch case for key input
# o = Option
# c = Calibration
# d = Debug
# q = Quit
def keyinput(i):
    def default():
        return
    def quit():
        global Running
        Running = False
    def calibrate():
        global Calibrate_Status
        if Calibrate_Status == 0:
            Calibrate_Status = 1
            Calibrate_Points()
    def debug():
        global DEBUG
        global CONF
        global Option_Menu_Open
        if DEBUG == True:
            DEBUG = False
            Option_Menu_Open = False
            cv2.destroyAllWindows()
        else:
            DEBUG = True
        CONF.SaveToJSON()
    switcher={
            111:Option_Colo_Open, # key 'o'
            99:calibrate, # key 'c'
            100:debug, # key 'd'
            113:quit, # key 'q'
            }
    switcher.get(i,default)()



def stackImages(scale,imgArray):
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
        hor_con = [imageBlank]*rows
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




#----------------------------------------------------------------#
#Start
#----------------------------------------------------------------#
global CONF
global CONF_OLD
CONF = Config();
CONF.LoadFromJSON()  # Load from config.conf file
CONF_OLD = CONF.copy() # Backup conf


cap = cv2.VideoCapture(0) # Set camera input
# Set img size of camera (x,y)
cap.set(3,CONF.CAMERA_X)
cap.set(4,CONF.CAMERA_Y)

MOUSE_PRESSED = 0
Running = True
while Running:
    success, img = cap.read() # Read img
    img = cv2.resize(img,(CONF.SCALE_X, CONF.SCALE_Y),interpolation=cv2.INTER_LINEAR) # Resize image

    #Warp image
    if Calibrate_Status == 0:
        pts1 = np.float32(CONF.CORNERS)
        pts2 = np.float32([[0,0],[CONF.SCALE_X+CONF.BORDER_BUFFER*2,0],[0,CONF.SCALE_Y+CONF.BORDER_BUFFER*2],[CONF.SCALE_X+CONF.BORDER_BUFFER*2,CONF.SCALE_Y+CONF.BORDER_BUFFER*2]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        img = cv2.warpPerspective(img,matrix,(CONF.SCALE_X+CONF.BORDER_BUFFER*2,CONF.SCALE_Y+CONF.BORDER_BUFFER*2))

    #HSV mask
    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    lower = np.array([CONF.MASK_COLORS[0],CONF.MASK_COLORS[2],CONF.MASK_COLORS[4]])
    upper= np.array([CONF.MASK_COLORS[1],CONF.MASK_COLORS[3],CONF.MASK_COLORS[5]])
    mask = cv2.inRange(imgHSV, lower, upper)  
    if not (CONF.BLUR == 0):
        blur = cv2.blur(mask, (CONF.BLUR,CONF.BLUR), cv2.BORDER_DEFAULT)
    else:
        blur = mask

    # Detect blobs.
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 100
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(blur)
    if CONF.DEBUG == True: # Draw the keypoints in image
        blank = np.zeros((1, 1))
        blobs = cv2.drawKeypoints(img, keypoints, blank, (255, 255, 255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
    # For each blob 
    for p in coordinates:
        x = CONF.SCALE_X-int(p[0])-1+CONF.BORDER_BUFFER
        y = int(p[1])-CONF.BORDER_BUFFER
        if CONF.DEBUG == True: # Write cordinates to the blob in the image
            text = str(x*CONF.SCALE_FACTOR_X) + "|" + str(y*CONF.SCALE_FACTOR_Y)
            blobs = cv2.putText(blobs, text, (int(p[0])+25,int(p[1])-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            if Option_Menu_Open == True:
                if cv2.getWindowProperty("Options",cv2.WND_PROP_VISIBLE) <= 0:
                    Option_Menu_Open = False

        # If calibration mode is enabled
        if Calibrate_Status > 0:
            Calibrate_Points(p[0], p[1])
        elif Option_Menu_Open == False:
            # Move mouse cursor to position
            mouse.move(int(x*CONF.SCALE_FACTOR_X), int(y* CONF.SCALE_FACTOR_Y))
            if(MOUSE_PRESSED == 0): # Press mouse button if mouse is not pressed
                #print("press")
                mouse.press(int(x*CONF.SCALE_FACTOR_X), int(y* CONF.SCALE_FACTOR_Y))
            MOUSE_PRESSED = 1
    
    # If mouse is pressed and no blob is detected for 5 times then release mouse
    if(MOUSE_PRESSED > 0 and len(coordinates) == 0):
        MOUSE_PRESSED +=1
        if(MOUSE_PRESSED > 5):
            #print("release")
            mouse.release(int(x*CONF.SCALE_FACTOR_X), int(y*CONF.SCALE_FACTOR_Y))
            MOUSE_PRESSED = 0

    # If debug mode is enabled, print image
    if CONF.DEBUG == True:
        debug_img = stackImages(0.5,([blobs,imgHSV],[mask,blur]))
        cv2.imshow('Debug', debug_img)

    keyinput(cv2.waitKey(1) & 0xFF)