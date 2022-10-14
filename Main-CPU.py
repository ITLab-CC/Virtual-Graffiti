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
from module.imageprocessing import ImageProcessing
from module.paint import Paint
from module.sound import Sound

global CONF
global CONF_OLD
global PAINT



# Close/exit/end/dead/kill/destroy/terminate/stop/quit/bye lol
def quitClean():
    global Running
    global IMAGEPROCESSING
    Running = False
    IMAGEPROCESSING.end()
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

global IMAGEPROCESSING
IMAGEPROCESSING = ImageProcessing(CONF, 2)

# Some vars
spraying = False
lastPos = False
lastTimeInput = False
# MOUSE_PRESSED = 0
    
try:
    Running = True
    while Running:
        
        keyinput(cv2.waitKey(1) & 0xFF)
        
        # Detect blobs.
        success, debug_img, coordinates, keypoints = IMAGEPROCESSING.grap_coordinates()
        if success == False:
            continue
        
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
        
        # Show debug image
        cv2.imshow('Debug', debug_img)
    
except KeyboardInterrupt:
    quitClean()