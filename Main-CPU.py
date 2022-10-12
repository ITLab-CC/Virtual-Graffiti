import cv2                   # OpenCV
import numpy as np           # Create arrays
import time                  # Mesure FPS
from tkinter import *        # Drawing
#import mouse                # Mouse control
#import pyautogui as mouse    # Mouse control
# from pynput.mouse import Button, Controller # Moving mouse
# mouse = Controller()
# from pymouse import PyMouse  # Moving mouse
# mouse = PyMouse()

from module.config import Config
from module.optionmenue import OptionMenue
from module.threadedcamera import ThreadedCamera
from module.paint import Paint
from module.sound import Sound

global CONF
global CONF_OLD
global PAINT


# #Convert hex to rgb
# def hex_to_rgb(value):
#     value = value.lstrip('#')
#     lv = len(value)
#     hex = [None] * 3
#     counter = 0
#     for i in range(0, lv, lv // 3):
#         hex[counter] = int(value[i:i + lv // 3], 16)
#         counter = counter + 1
#     return hex



# #convert rgb to hex
# def rgb_to_hex(rgb):
#     return '#%02x%02x%02x' % rgb



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
    


def quitClean():
    global Running
    Running = False
    cap.end()
    PAINT.End()
    cv2.destroyAllWindows()
    print("Goodbye")
    


#Switch case for key input
# o = Option
# c = Calibration
# d = Debug
# q = Quit
def keyinput(i):
    def default():
        return
    def quit():
        quitClean()
    def option_open():
        global OPTIONMENUE
        if OPTIONMENUE.isOpen():
            OPTIONMENUE.Close()
        else:
            OPTIONMENUE.Open()
    def calibrate():
        if CONF.Calibrate_Status == 0:
            CONF.Calibrate_Status = 1
            CONF.Calibrate_Points()
    def debug():
        global CONF
        CONF.DEBUG = not CONF.DEBUG
        if CONF.DEBUG == False:
            cv2.destroyAllWindows()
        CONF.SaveToJSON()
    def paint():
        global CONF
        CONF.PAINT_ENABLED = not CONF.PAINT_ENABLED
        if CONF.PAINT_ENABLED:
            PAINT.Show()
        else:
            PAINT.Hide()
        CONF.SaveToJSON()
    switcher={
            111:option_open, # key 'o'
            99:calibrate, # key 'c'
            100:debug, # key 'd'
            113:quit, # key 'q'
            112:paint, # key 'p
            }
    switcher.get(i,default)()
    
    
def Paint_key_init():
    global PAINT
    # Use keys when beeing in paint mode
    def tkInput(event):
        print("Key:", event.char)
        keyinput(ord(event.char))

    PAINT.tkScreen.bind("o", tkInput)
    PAINT.tkScreen.bind("c", tkInput)
    PAINT.tkScreen.bind("d", tkInput)
    PAINT.tkScreen.bind("q", tkInput)
    PAINT.tkScreen.bind("p", tkInput)

#----------------------------------------------------------------#
#Start
#----------------------------------------------------------------#
# global CONF
# global CONF_OLD
CONF = Config()
CONF.LoadFromJSON()  # Load from config.conf file
CONF_OLD = CONF.copy() # Backup conf

# Option Menue
global OPTIONMENUE
OPTIONMENUE = OptionMenue(CONF, CONF_OLD, "Options")

# global PAINT
PAINT = Paint(CONF.SPRAY_COLOUR, CONF.PAINT_ENABLED)
Paint_key_init()

# Sound
global SOUND
SOUND = Sound(CONF.SOUND_SPRAY_FILE)

# Some const vars
lower = np.array([CONF.MASK_COLORS[0],CONF.MASK_COLORS[2],CONF.MASK_COLORS[4]])
upper= np.array([CONF.MASK_COLORS[1],CONF.MASK_COLORS[3],CONF.MASK_COLORS[5]])
blank = np.zeros((1, 1))

# Some vars
spraying = False
prev_frame_time = 0
lastPos = False
lastTimeInput = False
# MOUSE_PRESSED = 0


#cap = cv2.VideoCapture(0) # Set camera input
cap = ThreadedCamera(CONF.CAMERA_X, CONF.CAMERA_Y, CONF.CAMERA_FPS, CONF.CAMERA_SRC, CONF.CV2_ALGORITHM_NUMBER)

try:
    Running = True
    while Running:
        img, captureFps = cap.grap_frame() # Read img
        if img is None:
            continue
        img = cv2.resize(img,(CONF.SCALE_X, CONF.SCALE_Y),interpolation=cv2.INTER_LINEAR) # Resize image

        #Warp image
        if CONF.Calibrate_Status == 0:
            pts1 = np.float32(CONF.CORNERS)
            pts2 = np.float32([[0,0],[CONF.SCALE_X+CONF.BORDER_BUFFER*2,0],[0,CONF.SCALE_Y+CONF.BORDER_BUFFER*2],[CONF.SCALE_X+CONF.BORDER_BUFFER*2,CONF.SCALE_Y+CONF.BORDER_BUFFER*2]])
            matrix = cv2.getPerspectiveTransform(pts1,pts2)
            img = cv2.warpPerspective(img,matrix,(CONF.SCALE_X+CONF.BORDER_BUFFER*2,CONF.SCALE_Y+CONF.BORDER_BUFFER*2))

        #HSV mask
        imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
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
            blobs = cv2.drawKeypoints(img, keypoints, blank, (255, 255, 255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            
            # show fps
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            fps = str(fps)
            fpsString = "FPS: " + fps + " Capture: " + str(captureFps)
            cv2.putText(blobs, fpsString, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
            
            # If debug mode is enabled, print image
            debug_img = stackImages(0.5,([blobs,imgHSV],[mask,blur]))
            cv2.imshow('Debug', debug_img)

        coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
        # For each blob
        for p in coordinates:
            lastTimeInput = time.time()
            blobSize = keypoints[0].size
            orgx = int(p[0])
            orgy = int(p[1])
            newx = CONF.SCALE_X-orgx+CONF.BORDER_BUFFER-1
            newy = orgy-CONF.BORDER_BUFFER
            realX = int(newx*CONF.SCALE_FACTOR_X)
            realY = int(newy*CONF.SCALE_FACTOR_Y)
            if CONF.DEBUG == True: # Write cordinates to the blob in the image
                text = str(realX) + "|" + str(realY)
                blobs = cv2.putText(blobs, text, (orgx+25,orgy-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

            # If calibration mode is enabled
            if CONF.Calibrate_Status > 0:
                CONF.Calibrate_Points(orgx, orgy)
            elif OPTIONMENUE.isOpen() == False:
                # Move mouse cursor to position
                if spraying == False:
                    if ((CONF.SCREEN_X-100) <= realX and (CONF.SCREEN_Y-100) <= realY):
                        CONF.DEBUG = True
                        CONF.SaveToJSON()
                        continue
                if CONF.PAINT_ENABLED:
                    if lastPos != False:
                        PAINT.createGrafittiLine(lastPos[0], lastPos[1], realX, realY, blobSize)
                        PAINT.createGrafittiLineBigger(lastPos[0], lastPos[1], realX, realY, blobSize)
                    lastPos = (realX, realY)
                # else:
                #     mouse.move(realX, realY)
                #     mouse.press(realX, realY)
                spraying = True
                SOUND.play()
                # Move mouse cursor to position
                # #mouse.move(int(x*CONF.SCALE_FACTOR_X), int(y* CONF.SCALE_FACTOR_Y))
                # #mouse.moveTo(int(x*CONF.SCALE_FACTOR_X), int(y* CONF.SCALE_FACTOR_Y), duration=0)
                # if(MOUSE_PRESSED == 0): # Press mouse button if mouse is not pressed
                #     print("press")
                #     #mouse.press(int(x*CONF.SCALE_FACTOR_X), int(y* CONF.SCALE_FACTOR_Y))
                #     #mouse.press(button='left')
                #     #mouse.press('left')
                #     #mouse.press(Button.left)
                #     #mouse.mouseDown()
                #     MOUSE_PRESSED = 1
        
        if lastTimeInput != False and time.time() - lastTimeInput > 0.5: # If no input for 0.5 seconds then stop drawing
            SOUND.stop()
            lastTimeInput = False
            if CONF.PAINT_ENABLED:
                lastPos = False
            # else:
            #     mouse.release(realX, realY)
            # MOUSE_PRESSED = 0
            spraying = False
        
        # If mouse is pressed and no blob is detected for 5 times then release mouse
        # if(MOUSE_PRESSED > 0 and len(coordinates) == 0):
        #     MOUSE_PRESSED +=1
        #     if(MOUSE_PRESSED > 5):
        #         print("release")
        #         #mouse.release(int(x*CONF.SCALE_FACTOR_X), int(y*CONF.SCALE_FACTOR_Y))
        #         #mouse.release(button='left')
        #         #mouse.release('left')
        #         #mouse.release(Button.left)
        #         #mouse.mouseUp()
        #         MOUSE_PRESSED = 0

        keyinput(cv2.waitKey(1) & 0xFF)
    
except KeyboardInterrupt:
    quitClean()