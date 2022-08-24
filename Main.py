from contextlib import nullcontext
from curses.ascii import NUL
from sys import call_tracing
from turtle import width
import cv2
import numpy as np
import json
from os.path import exists

#Default values
CONFIG_FILE="config.conf"
SCREEN_X=1920
SCREEN_Y=1080
CAMERA_X=1920
CAMERA_Y=1080
SCALE_X=SCREEN_X/2  #720
SCALE_Y=SCREEN_Y/2  #576
SCALE_X_OLD=SCREEN_X/2  #720
SCALE_Y_OLD=SCREEN_Y/2  #576
CORNERS=[[68,19],[655,50],[70,500],[640,508]]
MASK_COLORS=[0, 179, 0, 255, 0, 145, 1]
MASK_COLORS_OLD=[0, 179, 0, 255, 0, 145, 1]

def SaveToJSON():
    global SCREEN_X
    global SCREEN_Y
    global CAMERA_X
    global CAMERA_Y
    global SCALE_X
    global SCALE_Y
    global CORNERS
    global MASK_COLORS
    global CONFIG_FILE
    data = {
        'config' : {
            'SCREEN_X' : SCREEN_X,
            'SCREEN_Y' : SCREEN_Y,
            'CAMERA_X' : CAMERA_X,
            'CAMERA_Y' : CAMERA_Y,
            'SCALE_X' : SCALE_X,
            'SCALE_Y' : SCALE_Y,
            'CORNERS' : CORNERS,
            'MASK_COLORS' : MASK_COLORS
        }
    }
    with open(CONFIG_FILE, 'w') as outfile:
        json.dump(data, outfile)

def LoadFromJSON():
    global SCREEN_X
    global SCREEN_Y
    global CAMERA_X
    global CAMERA_Y
    global SCALE_X
    global SCALE_Y
    global CORNERS
    global MASK_COLORS
    global CONFIG_FILE
    if not exists(CONFIG_FILE):
        SaveToJSON()
    try:
        with open(CONFIG_FILE) as json_file:
            data = json.load(json_file)
            SCREEN_X = data['config']['SCREEN_X']
            SCREEN_Y = data['config']['SCREEN_Y']
            CAMERA_X = data['config']['CAMERA_X']
            CAMERA_Y = data['config']['CAMERA_Y']
            SCALE_X = data['config']['SCALE_X']
            SCALE_Y = data['config']['SCALE_Y']
            CORNERS = data['config']['CORNERS']
            MASK_COLORS = data['config']['MASK_COLORS']
    except:
        print("The config has a wrong format. Delete the file and a new one will be generated")

LoadFromJSON()

cap = cv2.VideoCapture(0)
cap.set(3,CAMERA_X)
cap.set(4,CAMERA_Y)

def setTrackbarPos(x):
    global SCALE_X
    global SCALE_Y
    global MASK_COLORS
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
        if MASK_COLORS[6] < 1:
            cv2.setTrackbarPos("Blur","Options", 1)
            MASK_COLORS[6] = 1
        SaveToJSON()
    except:
        return;
def Button_Reset(x):
    global MASK_COLORS
    global MASK_COLORS_OLD
    global SCALE_X_OLD
    global SCALE_X
    global SCALE_Y_OLD
    global SCALE_Y
    if(x == 1):
        MASK_COLORS=MASK_COLORS_OLD.copy()
        SCALE_X = SCALE_X_OLD
        SCALE_Y = SCALE_Y_OLD
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
        print("Reseted to: ", MASK_COLORS[0],MASK_COLORS[1],MASK_COLORS[2],MASK_COLORS[3],MASK_COLORS[4],MASK_COLORS[5],MASK_COLORS[6])

def Option_Colo_Open():
    cv2.destroyWindow("Options")
    global MASK_COLORS
    global MASK_COLORS_OLD
    global SCALE_X_OLD
    global SCALE_X
    global SCALE_Y_OLD
    global SCALE_Y
    global CAMERA_X
    global CAMERA_Y
    cv2.namedWindow("Options")
    cv2.resizeWindow("Options",300,240)
    cv2.createTrackbar("Scale X","Options",SCALE_X,CAMERA_X, setTrackbarPos)
    cv2.createTrackbar("Scale Y","Options",SCALE_Y,CAMERA_Y,setTrackbarPos)
    cv2.createTrackbar("Hue Min","Options",MASK_COLORS[0],255, setTrackbarPos)
    cv2.createTrackbar("Hue Max","Options",MASK_COLORS[1],255,setTrackbarPos)
    cv2.createTrackbar("Sat Min","Options", MASK_COLORS[2],255, setTrackbarPos)
    cv2.createTrackbar("Sat Max","Options",MASK_COLORS[3],255,setTrackbarPos)
    cv2.createTrackbar("Val Min","Options",MASK_COLORS[4],255, setTrackbarPos)
    cv2.createTrackbar("Val Max","Options",MASK_COLORS[5],255,setTrackbarPos)
    cv2.createTrackbar("Blur","Options",MASK_COLORS[6],20,setTrackbarPos)
    cv2.createTrackbar("Reset","Options",0,1,Button_Reset)
    MASK_COLORS_OLD=MASK_COLORS.copy()
    SCALE_X_OLD = SCALE_X
    SCALE_Y_OLD = SCALE_Y

Calibrate_Status = 0
def Calibrate_Points(x, y):
    global Calibrate_Status

    cal_imag = np.zeros((SCREEN_Y,SCREEN_X,3), np.uint8)

    if Calibrate_Status == 1:
        # print(str(x) + "<" + str(int(SCALE_X/2)) + " and " + str(y) + "<" + str(int(SCALE_Y/2)))
        cv2.circle(cal_imag,(0,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,15), 15, (255,0,0), -1)
        if((x < int(SCALE_X/2)) and (y < int(SCALE_Y/2))):
            CORNERS[0][0] = x-20
            CORNERS[0][1] = y-20
            Calibrate_Status = 2
    elif Calibrate_Status == 2:
        cv2.circle(cal_imag,(SCREEN_X-1,0), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(SCREEN_X-16,15), 15, (255,0,0), -1)
        if((x > int(SCALE_X/2)) and (y < int(SCALE_Y/2))):
            CORNERS[1][0] = x+20
            CORNERS[1][1] = y-20
            Calibrate_Status = 3
    elif Calibrate_Status == 3:
        cv2.circle(cal_imag,(0,SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(15,SCREEN_Y-16), 15, (255,0,0), -1)
        if((x < int(SCALE_X/2)) and (y > int(SCALE_Y/2))):
            CORNERS[2][0] = x-20
            CORNERS[2][1] = y+20
            Calibrate_Status = 4
    elif Calibrate_Status == 4:
        cv2.circle(cal_imag,(SCREEN_X-1,SCREEN_Y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(SCREEN_X-16,SCREEN_Y-16), 15, (255,0,0), -1)
        if((x > int(SCALE_X/2)) and (y > int(SCALE_Y/2))):
            CORNERS[3][0] = x+20
            CORNERS[3][1] = y+20
            Calibrate_Status = 0

    cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Calibrate", cal_imag)
    if Calibrate_Status == 0:
        SaveToJSON()
        cv2.destroyWindow("Calibrate")



Running = True

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
    switcher={
            111:Option_Colo_Open,
            99:calibrate,
            113:quit,
            }
    switcher.get(i,default)()

while Running:
    success, img = cap.read()
    img = cv2.resize(img,(SCALE_X, SCALE_Y),interpolation=cv2.INTER_LINEAR)
    img = cv2.flip(img, 1)

    if Calibrate_Status == 0:
        pts1 = np.float32(CORNERS)
        pts2 = np.float32([[0,0],[SCALE_X,0],[0,SCALE_Y],[SCALE_X,SCALE_Y]])
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
        img = cv2.warpPerspective(img,matrix,(SCALE_X,SCALE_Y))

    # cv2.imshow("Output",imgOutput)



    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    #print(MASK_COLORS[0],MASK_COLORS[1],MASK_COLORS[2],MASK_COLORS[3],MASK_COLORS[4],MASK_COLORS[5],MASK_COLORS[6])


    lower = np.array([MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4]])
    upper= np.array([MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5]])
    mask = cv2.inRange(imgHSV, lower, upper)  
    blur = cv2.blur(mask, (MASK_COLORS[6],MASK_COLORS[6]), cv2.BORDER_DEFAULT)

    # contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# #contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)

    # #Bestimmung der Mitte
    # for cnt in contours:
    #     cv2.drawContours(mask,cnt,-1,(0,88,0),3)
    #     print(cv2.contourArea(cnt))
	# 	# (x, y, w, h) = cv2.boundingRect(cnt)
	# 	# x_medium = int(((x+x+w)/2))
	# 	# y_medium = int(((y+y+h)/2))

    # detector = cv2.SimpleBlobDetector()

    # Detect blobs.
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 100
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(blur)
    blank = np.zeros((1, 1))
    blobs = cv2.drawKeypoints(img, keypoints, blank, (0, 0, 255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    coordinates = cv2.KeyPoint_convert(keypoints)
    #print(coordinates)
    pts = np.asarray([[p[0], p[1]] for p in coordinates])
    for p in coordinates:
        x = int(p[0])
        y = int(p[1])
        text = str(x) + "|" + str(y)
        blobs = cv2.putText(blobs, text, (x+10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
        if Calibrate_Status > 0:
            Calibrate_Points(x, y)
    # if()
    # print(pts[0][0])
    # text = ("Text")
    

    cv2.imshow("Blobs", blobs)

    #cv2.imshow("Original",img)
    # cv2. imshow("HSV",imgHSV)
    #cv2.imshow("Mask", mask)

    keyinput(cv2.waitKey(1) & 0xFF)
    # print(ord('q')) #113
    # print(ord('o')) #111
    # if cv2.waitKey(1) & 0xFF ==ord('q'):
    #     break
