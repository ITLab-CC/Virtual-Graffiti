import cv2                   # OpenCV
import time                  # Mesure FPS
from tkinter import *        # Drawing

from module.config import Config
from module.optionmenue import OptionMenue
from module.imageprocessing import ImageProcessing
from module.paint import Paint
# from module.sound import Sound
from module.mouse import Mouse

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


global old_Frame
global new_Frame
old_Frame = time.time()
new_Frame = time.time()
def getFPS():
    global old_Frame
    global new_Frame
    new_Frame = time.time()
    fps = 1/(new_Frame-old_Frame)
    old_Frame = new_Frame
    return int(fps)



#----------------------------------------------------------------#
#Start
#----------------------------------------------------------------#
# global CONF
# global CONF_OLD
CONF = Config()
CONF.LoadFromJSON()  # Load from config.conf file
CONF_OLD = CONF.copy() # Backup conf
MOUSE = Mouse(CONF.SCREEN_X, CONF.SCREEN_Y)         # Create Objekt

# Option Menue
global OPTIONMENUE
OPTIONMENUE = OptionMenue(CONF, CONF_OLD, "Options")

# global PAINT
PAINT = Paint(CONF.SPRAY_COLOUR, CONF.PAINT_ENABLED)
Paint_key_init()

# Sound
# global SOUND
# SOUND = Sound(CONF.SOUND_SPRAY_FILE)

global IMAGEPROCESSING
IMAGEPROCESSING = ImageProcessing(CONF, 1)

# Some vars
spraying = False
lastPos = False
lastTimeInput = False
blobSizeMax = 60
blobSizeMin = 15
# MOUSE_PRESSED = 0
    
try:
    Running = True
    while Running:
        
        keyinput(cv2.waitKey(1) & 0xFF)
        
        if lastTimeInput != False and time.time() - lastTimeInput > 0.1: # If no input for 0.5 seconds then stop drawing
            # SOUND.stop()
            lastTimeInput = False
            if CONF.PAINT_ENABLED:
                lastPos = False
            else:
                # MOUSE.release(realX, realY)
                MOUSE.release()
                # MOUSE.press(0,0)
            spraying = False
        
        # Detect blobs.
        success, debug_img, coordinates, blobSizes = IMAGEPROCESSING.grap_coordinates()
        if success == False:
            continue
        
        # Show debug image
        if CONF.DEBUG:
            cv2.imshow('Debug', debug_img)
            # print("FPS:" + str(getFPS()))
        
        # For each blob
        if len(coordinates) != 0:
            counter = 0
            lastTimeInput = time.time()
            for p in coordinates:
                blobSize = blobSizes[counter]
                # print(blobSize)
                # if (blobSize > blobSizeMax) and (blobSize < 80):
                #     blobSizeMax = blobSize
                # if (blobSize < blobSizeMin) and (blobSize > 40):
                #     blobSizeMin = blobSize
                orgx = int(p[0])
                orgy = int(p[1])
                # newx = CONF.SCALE_X-orgx+CONF.BORDER_BUFFER-1
                newx = CONF.SCALE_X-orgx
                # newy = orgy-CONF.BORDER_BUFFER
                newy = orgy
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
                            # PAINT.Draw(realX, realY, blobSize)
                        lastPos = (realX, realY)
                    else:
                        # print(spraying)
                        # MOUSE.move(realX, realY)
                        if spraying == False:
                            # MOUSE.press(realX, realY, (0,0), 15, 0, Config.SCREEN_X/2)
                            MOUSE.press(realX, realY)
                        MOUSE.move(realX, realY)
                        
                    spraying = True
                counter += 1
            
            # SOUND.play()
            PAINT.Screen_Update()
                
except KeyboardInterrupt:
    quitClean()