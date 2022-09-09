import cv2
import numpy as np
import json
from os.path import exists
import mss
from pymouse import PyMouse
import time
import pygame

mouse = PyMouse()

#Default values. Will be loaded from config.conf file
DEBUG = False
CONFIG_FILE="config.conf"
sct=mss.mss()
SCREEN_X=int(sct.monitors[1]['width'])
SCREEN_Y=int(sct.monitors[1]['height'])
CAMERA_X=1920
CAMERA_Y=1080
SCALE_X=int(SCREEN_X/2)
SCALE_Y=int(SCREEN_Y/2)
SCALE_X_OLD=SCALE_X
SCALE_Y_OLD=SCALE_Y
SCALE_FACTOR_X = SCREEN_X/SCALE_X
SCALE_FACTOR_Y = SCREEN_Y/SCALE_Y
CORNERS=[[77, 7], [897, 25], [81, 501], [870, 517]]
MASK_COLORS=[0, 179, 0, 255, 0, 145, 1]
MASK_COLORS_OLD=MASK_COLORS
BORDER_BUFFER=20
BORDER_BUFFER_OLD=BORDER_BUFFER
MOUSE_PRESSED_TIME = 4
MOUSE_PRESSED_TIME_OLD = MOUSE_PRESSED_TIME



#Save vars to config.conf file
def SaveToJSON():
    global DEBUG
    global SCREEN_X
    global SCREEN_Y
    global CAMERA_X
    global CAMERA_Y
    global SCALE_X
    global SCALE_Y
    global CORNERS
    global MASK_COLORS
    global CONFIG_FILE
    global BORDER_BUFFER
    global MOUSE_PRESSED_TIME
    data = {
        'config' : {
            'DEBUG': DEBUG,
            'SCREEN_X' : SCREEN_X,
            'SCREEN_Y' : SCREEN_Y,
            'CAMERA_X' : CAMERA_X,
            'CAMERA_Y' : CAMERA_Y,
            'SCALE_X' : SCALE_X,
            'SCALE_Y' : SCALE_Y,
            'CORNERS' : CORNERS,
            'MASK_COLORS' : MASK_COLORS,
            'BORDER_BUFFER' : BORDER_BUFFER,
            'MOUSE_PRESSED_TIME' : MOUSE_PRESSED_TIME
        }
    }
    with open(CONFIG_FILE, 'w') as outfile:
        json.dump(data, outfile)

#Load vars from config.conf file
def LoadFromJSON():
    global DEBUG
    global SCREEN_X
    global SCREEN_Y
    global CAMERA_X
    global CAMERA_Y
    global SCALE_X
    global SCALE_Y
    global CORNERS
    global MASK_COLORS
    global CONFIG_FILE
    global SCALE_FACTOR_X
    global SCALE_FACTOR_Y
    global BORDER_BUFFER
    global MOUSE_PRESSED_TIME
    if not exists(CONFIG_FILE):
        SaveToJSON()
    try:
        with open(CONFIG_FILE) as json_file:
            data = json.load(json_file)
            DEBUG = data['config']['DEBUG']
            if DEBUG == "true":
                DEBUG = True
            if DEBUG == "false":
                DEBUG = False
            SCREEN_X = data['config']['SCREEN_X']
            SCREEN_Y = data['config']['SCREEN_Y']
            CAMERA_X = data['config']['CAMERA_X']
            CAMERA_Y = data['config']['CAMERA_Y']
            SCALE_X = data['config']['SCALE_X']
            SCALE_Y = data['config']['SCALE_Y']
            CORNERS = data['config']['CORNERS']
            MASK_COLORS = data['config']['MASK_COLORS']
            BORDER_BUFFER = data['config']['BORDER_BUFFER']
            SCALE_FACTOR_X = SCREEN_X/SCALE_X
            SCALE_FACTOR_Y = SCREEN_Y/SCALE_Y
            MOUSE_PRESSED_TIME = data['config']['MOUSE_PRESSED_TIME']
    except:
        print("The config has a wrong format. Delete the file and a new one will be generated")



#Options menu
def setTrackbarPos(x):
    global SCALE_X
    global SCALE_Y
    global MASK_COLORS
    global SCALE_FACTOR_X
    global SCALE_FACTOR_Y
    global BORDER_BUFFER
    global MOUSE_PRESSED_TIME
    try:
        SCALE_X = cv2.getTrackbarPos("Scale X","Options")
        SCALE_Y = cv2.getTrackbarPos("Scale Y","Options")
        MASK_COLORS[0] = cv2.getTrackbarPos("Hue Min","Options")
        MASK_COLORS[1] = cv2.getTrackbarPos("Hue Max","Options")
        MASK_COLORS[2] = cv2.getTrackbarPos("Sat Min","Options")
        MASK_COLORS[3] = cv2.getTrackbarPos("Sat Max","Options")
        MASK_COLORS[4] = cv2.getTrackbarPos("Val Min","Options")
        MASK_COLORS[5] = cv2.getTrackbarPos("Val Max","Options")
        MASK_COLORS[6] = cv2.getTrackbarPos("Blur","Options")
        BORDER_BUFFER = cv2.getTrackbarPos("Boarder Buffer","Options")
        MOUSE_PRESSED_TIME = cv2.getTrackbarPos("Mouse Pressed Time","Options")
        if MASK_COLORS[6] < 1:
            cv2.setTrackbarPos("Blur","Options", 1)
            MASK_COLORS[6] = 1
        SaveToJSON()
        SCALE_FACTOR_X = SCREEN_X/SCALE_X
        SCALE_FACTOR_Y = SCREEN_Y/SCALE_Y
    except:
        return;

def Button_Reset(x):
    global MASK_COLORS
    global MASK_COLORS_OLD
    global SCALE_X_OLD
    global SCALE_X
    global SCALE_Y_OLD
    global SCALE_Y
    global BORDER_BUFFER
    global BORDER_BUFFER_OLD
    global MOUSE_PRESSED_TIME
    global MOUSE_PRESSED_TIME_OLD
    if(x == 1):
        MASK_COLORS=MASK_COLORS_OLD.copy()
        SCALE_X = SCALE_X_OLD
        SCALE_Y = SCALE_Y_OLD
        BORDER_BUFFER = BORDER_BUFFER_OLD
        MOUSE_PRESSED_TIME = MOUSE_PRESSED_TIME_OLD
        cv2.setTrackbarPos("Scale X","Options", SCALE_X)
        cv2.setTrackbarPos("Scale Y","Options", SCALE_Y)
        cv2.setTrackbarPos("Hue Min","Options", MASK_COLORS[0])
        cv2.setTrackbarPos("Hue Max","Options", MASK_COLORS[1])
        cv2.setTrackbarPos("Sat Min","Options", MASK_COLORS[2])
        cv2.setTrackbarPos("Sat Max","Options", MASK_COLORS[3])
        cv2.setTrackbarPos("Val Min","Options", MASK_COLORS[4])
        cv2.setTrackbarPos("Val Max","Options", MASK_COLORS[5])
        cv2.setTrackbarPos("Blur","Options", MASK_COLORS[6])
        cv2.setTrackbarPos("Reset","Options", 0)
        cv2.setTrackbarPos("Boarder Buffer", BORDER_BUFFER)
        cv2.setTrackbarPos("Mouse Pressed Time", MOUSE_PRESSED_TIME)
        print("Reseted to: ", MASK_COLORS[0],MASK_COLORS[1],MASK_COLORS[2],MASK_COLORS[3],MASK_COLORS[4],MASK_COLORS[5],MASK_COLORS[6])

# Open/Create options menu
Option_Menu_Open = False
def Option_Colo_Open():
    if cv2.getWindowProperty("Options",cv2.WND_PROP_VISIBLE) <= 0:
        global MASK_COLORS
        global MASK_COLORS_OLD
        global SCALE_X_OLD
        global SCALE_X
        global SCALE_Y_OLD
        global SCALE_Y
        global CAMERA_X
        global CAMERA_Y
        global BORDER_BUFFER
        global BORDER_BUFFER_OLD
        global Option_Menu_Open
        global MOUSE_PRESSED_TIME
        Option_Menu_Open = True
        cv2.namedWindow("Options")
        cv2.resizeWindow("Options",300,600)
        cv2.createTrackbar("Scale X","Options",SCALE_X,CAMERA_X, setTrackbarPos)
        cv2.createTrackbar("Scale Y","Options",SCALE_Y,CAMERA_Y,setTrackbarPos)
        cv2.createTrackbar("Hue Min","Options",MASK_COLORS[0],255, setTrackbarPos)
        cv2.createTrackbar("Hue Max","Options",MASK_COLORS[1],255,setTrackbarPos)
        cv2.createTrackbar("Sat Min","Options", MASK_COLORS[2],255, setTrackbarPos)
        cv2.createTrackbar("Sat Max","Options",MASK_COLORS[3],255,setTrackbarPos)
        cv2.createTrackbar("Val Min","Options",MASK_COLORS[4],255, setTrackbarPos)
        cv2.createTrackbar("Val Max","Options",MASK_COLORS[5],255,setTrackbarPos)
        cv2.createTrackbar("Blur","Options",MASK_COLORS[6],20,setTrackbarPos)
        cv2.createTrackbar("Boarder Buffer","Options", BORDER_BUFFER,50,setTrackbarPos)
        cv2.createTrackbar("Reset","Options",0,1,Button_Reset)
        cv2.createTrackbar("Mouse Pressed Time","Options",MOUSE_PRESSED_TIME,10,setTrackbarPos)
        MASK_COLORS_OLD=MASK_COLORS.copy()
        SCALE_X_OLD = SCALE_X
        SCALE_Y_OLD = SCALE_Y
        BORDER_BUFFER_OLD = BORDER_BUFFER



#Camera adjust
def align_camera(x, y):
    global CAMERA_X
    global CAMERA_Y
    global Running
    if x > CAMERA_X or x < 0:
        print(x)
        print("Align Camera X")
        Running = False
    if y > CAMERA_Y or y < 0:
        print("Align Camera Y")
        Running = False



#Calibration mode
Calibrate_Status = 0
def Calibrate_Points(x, y):
    global Calibrate_Status

    cal_imag = np.zeros((SCREEN_Y,SCREEN_X,3), np.uint8)

    if Calibrate_Status == 1:
        cv2.circle(cal_imag,(0,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,15), 15, (255,0,0), -1)
        if((x > int(SCALE_X/2)) and (y < int(SCALE_Y/2))):
            align_camera((x*SCALE_FACTOR_X)+BORDER_BUFFER, (y*SCALE_FACTOR_Y)-BORDER_BUFFER)
            CORNERS[1][0] = x+BORDER_BUFFER
            CORNERS[1][1] = y-BORDER_BUFFER
            Calibrate_Status = 2
    elif Calibrate_Status == 2:
        cv2.circle(cal_imag,(SCREEN_X-1,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(SCREEN_X-16,15), 15, (255,0,0), -1)
        if((x < int(SCALE_X/2)) and (y < int(SCALE_Y/2))):
            align_camera((x*SCALE_FACTOR_X)+BORDER_BUFFER, (y*SCALE_FACTOR_Y)-BORDER_BUFFER)
            CORNERS[0][0] = x-BORDER_BUFFER
            CORNERS[0][1] = y-BORDER_BUFFER
            Calibrate_Status = 3
    elif Calibrate_Status == 3:
        cv2.circle(cal_imag,(0,SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,SCREEN_Y-16), 15, (255,0,0), -1)
        if((x > int(SCALE_X/2)) and (y > int(SCALE_Y/2))):
            align_camera((x*SCALE_FACTOR_X)+BORDER_BUFFER, (y*SCALE_FACTOR_Y)-BORDER_BUFFER)
            CORNERS[3][0] = x+BORDER_BUFFER
            CORNERS[3][1] = y+BORDER_BUFFER
            Calibrate_Status = 4
    elif Calibrate_Status == 4:
        cv2.circle(cal_imag,(SCREEN_X-1,SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(SCREEN_X-16,SCREEN_Y-16), 15, (255,0,0), -1)
        if((x < int(SCALE_X/2)) and (y > int(SCALE_Y/2))):
            align_camera((x*SCALE_FACTOR_X)+BORDER_BUFFER, (y*SCALE_FACTOR_Y)-BORDER_BUFFER)
            CORNERS[2][0] = x-BORDER_BUFFER
            CORNERS[2][1] = y+BORDER_BUFFER
            Calibrate_Status = 0

    cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Calibrate", cal_imag)
    if Calibrate_Status == 0:
        SaveToJSON()
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
            Calibrate_Points(SCREEN_X,SCREEN_Y)
    def debug():
        global DEBUG
        if DEBUG == True:
            DEBUG = False
            Option_Menu_Open = False
            cv2.destroyAllWindows()
        else:
            DEBUG = True
        SaveToJSON()
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
LoadFromJSON() # Load from config.conf file

cap = cv2.VideoCapture(0) # Set camera input
# Set img size of camera (x,y)
cap.set(3,CAMERA_X)
cap.set(4,CAMERA_Y)

MOUSE_PRESSED = 0
Running = True
pygame.mixer.init()
pygame.mixer.music.load("sounds/spray.mp3")
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.pause()
spray = False
while Running:
    success, img = cap.read() # Read img
    img = cv2.resize(img,(SCALE_X, SCALE_Y),interpolation=cv2.INTER_LINEAR) # Resize image

    #Warp image
    if Calibrate_Status == 0:
        pts1 = np.float32(CORNERS)
        pts2 = np.float32([[0,0],[SCALE_X+BORDER_BUFFER*2,0],[0,SCALE_Y+BORDER_BUFFER*2],[SCALE_X+BORDER_BUFFER*2,SCALE_Y+BORDER_BUFFER*2]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        img = cv2.warpPerspective(img,matrix,(SCALE_X+BORDER_BUFFER*2,SCALE_Y+BORDER_BUFFER*2))

    #HSV mask
    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    lower = np.array([MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4]])
    upper= np.array([MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5]])
    mask = cv2.inRange(imgHSV, lower, upper)  
    if not (MASK_COLORS[6] == 0):
        blur = cv2.blur(mask, (MASK_COLORS[6],MASK_COLORS[6]), cv2.BORDER_DEFAULT)
    else:
        blur = mask

    # Detect blobs.
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 100
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(blur)
    if DEBUG == True: # Draw the keypoints in image
        blank = np.zeros((1, 1))
        blobs = cv2.drawKeypoints(img, keypoints, blank, (255, 255, 255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
    # For each blob 
    for p in coordinates:
        x = SCALE_X-int(p[0])-1+BORDER_BUFFER
        y = int(p[1])-BORDER_BUFFER
        if DEBUG == True: # Write cordinates to the blob in the image
            text = str(x*SCALE_FACTOR_X) + "|" + str(y*SCALE_FACTOR_Y)
            blobs = cv2.putText(blobs, text, (int(p[0])+25,int(p[1])-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                # If debug mode is enabled, print image
            debug_img = stackImages(0.5,([blobs,imgHSV],[mask,blur]))
            cv2.imshow('Debug', debug_img)
            if Option_Menu_Open == True:
                if cv2.getWindowProperty("Options",cv2.WND_PROP_VISIBLE) <= 0:
                    Option_Menu_Open = False

        # If calibration mode is enabled
        if Calibrate_Status > 0:
            Calibrate_Points(p[0], p[1])
        elif Option_Menu_Open == False:
            # Move mouse cursor to position
            mouse.move(int(x*SCALE_FACTOR_X), int(y* SCALE_FACTOR_Y))
            if(MOUSE_PRESSED == 0): # Press mouse button if mouse is not pressed
                #Activate debugmode in the bottom right corner
                if ((SCREEN_X-100) <= int(x*SCALE_FACTOR_X) and (SCREEN_Y-100) <= int(y* SCALE_FACTOR_Y) and spray == False):
                    DEBUG = True
                    pygame.mixer.music.pause()
                else:
                    mouse.press(int(x*SCALE_FACTOR_X), int(y* SCALE_FACTOR_Y))
                    MOUSE_PRESSED = 1
                    pygame.mixer.music.unpause()
                    spray = True
            elif (spray and len(coordinates) == 1):
                pygame.mixer.music.unpause()
    
    # If mouse is pressed and no blob is detected for 5 times then release mouse
    if(MOUSE_PRESSED > 0 and len(coordinates) == 0):
        MOUSE_PRESSED +=1
        pygame.mixer.music.pause()
        if(MOUSE_PRESSED > MOUSE_PRESSED_TIME):
            #print("release")
            mouse.release(int(x*SCALE_FACTOR_X), int(y* SCALE_FACTOR_Y))
            MOUSE_PRESSED = 0
            spray = False

    keyinput(cv2.waitKey(1) & 0xFF)