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



# Close/exit/end/dead/kill/destroy/terminate/stop/quit/bye lol
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
    
def tkInput(event):
    print("Key:", event.char)
    keyinput(ord(event.char))
    
def Paint_key_init():
    global PAINT
    # Use keys when beeing in paint mode
    PAINT.tkScreen.bind("o", tkInput)
    PAINT.tkScreen.bind("c", tkInput)
    PAINT.tkScreen.bind("d", tkInput)
    PAINT.tkScreen.bind("q", tkInput)
    PAINT.tkScreen.bind("p", tkInput)



# OpenCV2: Process picture
# Resize img
def Resize_img(img, x, y):
    return cv2.resize(img,(x, y),interpolation=cv2.INTER_LINEAR) # Resize image

# Warp img
def Warp_img(img, corners, scale_x, scale_y, boarder_buffer):
    pts1 = np.float32(corners)
    pts2 = np.float32([[0,0],[scale_x+boarder_buffer*2,0],[0,scale_y+boarder_buffer*2],[scale_x+boarder_buffer*2,scale_y+boarder_buffer*2]])
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(img,matrix,(scale_x+boarder_buffer*2,scale_y+boarder_buffer*2))

# HSV mask
def HSV_img(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

# Mask1
def Mask_img(img, lower, upper):
    return cv2.inRange(img, lower, upper)

# Blur img
def Blur_img(img, blur):
    if blur == 0:
        return img
    return cv2.blur(img, (blur,blur), cv2.BORDER_DEFAULT)

# Detect blobs
def Detect_blob(img, minArea = 100):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = minArea
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img) # keypoints
    coordinates = cv2.KeyPoint_convert(keypoints) # convert keypoints to coordinates
    return coordinates, keypoints

# Draw circle around blob
Blank = np.zeros((1, 1))
def Draw_blobs(img, keypoints, color=(255, 255, 255)):
    return cv2.drawKeypoints(img, keypoints, Blank, color,cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Write blob coordinates to img
def Draw_coordinates(img, orgx, orgy, text, color=(255, 255, 255)):
    return cv2.putText(img, text, (orgx+25,orgy-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

# Write FPS to img
prev_frame_time = 0
new_frame_time = 0
def Show_FPS(img, captureFps=-1):
    global prev_frame_time
    global new_frame_time
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)
    fps = str(fps)
    fpsString = "FPS: " + fps + " Capture: " + str(captureFps)
    cv2.putText(img, fpsString, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

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

# Some vars
spraying = False
lastPos = False
lastTimeInput = False
# MOUSE_PRESSED = 0


# Set camera input
cap = ThreadedCamera(CONF.CAMERA_X, CONF.CAMERA_Y, CONF.CAMERA_FPS, CONF.CAMERA_SRC, CONF.CV2_ALGORITHM_NUMBER)
    
try:
    Running = True
    while Running:
        img, captureFps = cap.grap_frame() # Read img
        if img is None:
            continue

        img = Resize_img(img, CONF.SCALE_X, CONF.SCALE_Y) # Resize image

        #Warp image
        if CONF.Calibrate_Status == 0:
            img = Warp_img(img, CONF.CORNERS, CONF.SCALE_X, CONF.SCALE_Y, CONF.BORDER_BUFFER)

        #HSV mask
        imgHSV = HSV_img(img)
        mask = Mask_img(imgHSV, Config.MASK_LOWER, Config.MASK_UPPER)
        
        blur = Blur_img(mask, CONF.BLUR)

        # Detect blobs.
        coordinates, keypoints = Detect_blob(blur, 100)

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
                
            if CONF.DEBUG == True: # Write cordinates to the blob in the image
                text = str(orgx) + "|" + str(orgy)
                img = Draw_coordinates(img, orgx, orgy, text, (255, 255, 255))
        
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

        if CONF.DEBUG == True: # Draw the keypoints in image
            img = Draw_blobs(img, keypoints, (255, 255, 255))
            
            # show fps
            Show_FPS(img, captureFps)

            # If debug mode is enabled, print image
            try:
                debug_img = Stack_img(0.5,([img,imgHSV],[mask,blur]))
                cv2.imshow('Debug', debug_img)
            except:
                cv2.imshow('blobs', img)
                cv2.imshow('imgHSV', imgHSV)
                cv2.imshow('mask', mask)
                cv2.imshow('blur', blur)

        keyinput(cv2.waitKey(1) & 0xFF)
    
except KeyboardInterrupt:
    quitClean()