import cv2                   # OpenCV
import json                  # Read write config as json
import mss                   # Get the screen size
import platform              # Get host platform (MacOS/Windows/Linux)
from os.path import exists   # If file exists
import numpy as np           # Create arrays

class Config:
    DEBUG = True
    PAINT_ENABLED = True
    CONFIG_FILE="config2.conf"
    SOUND_SPRAY_FILE="sounds/spray.mp3"
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
    SPRAY_COLOUR="#00FF00"
    
    # def <c(self):
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
                'PAINT_ENABLED' : self.PAINT_ENABLED,
                'SCREEN_X' : self.SCREEN_X,
                'SCREEN_Y' : self.SCREEN_Y,
                'CAMERA_X' : self.CAMERA_X,
                'CAMERA_Y' : self.CAMERA_Y,
                'SCALE_X' : self.SCALE_X,
                'SCALE_Y' : self.SCALE_Y,
                'CORNERS' : self.CORNERS,
                'MASK_COLORS' : self.MASK_COLORS,
                'BLUR' : self.BLUR,
                'BORDER_BUFFER' : self.BORDER_BUFFER,
                'SPRAY_COLOUR' : self.SPRAY_COLOUR                
            }
        }
        with open(self.CONFIG_FILE, 'w') as outfile:
            json.dump(data, outfile)

    #Load vars from config.conf file
    def LoadFromJSON(self):
        if not exists(self.CONFIG_FILE):
            self.SaveToJSON()
            return
        temp_old = self.copy()
        try:
            with open(self.CONFIG_FILE) as json_file:
                data = json.load(json_file)
                self.DEBUG = data['config']['DEBUG']
                self.PAINT_ENABLED = data['PAINT_ENABLED']['PAINT_ENABLED']
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
                self.SPRAY_COLOUR = data['config']['SPRAY_COLOUR']
        except:
            print("The config has a wrong format. Delete the file and a new one will be generated")
            self = temp_old

    #Calibration mode
    Calibrate_Status = 0
    def Calibrate_Points(self, x=-1, y=-1):
        if x < 0:
            x = self.SCREEN_X
        if y < 0:
            y = self.SCREEN_Y

        cal_imag = np.zeros((self.SCREEN_Y,self.SCREEN_X,3), np.uint8)

        if self.Calibrate_Status == 1:
            cv2.circle(cal_imag,(0,0), 50, (0,0,255), -1)
            cv2.circle(cal_imag,(15,15), 15, (255,0,0), -1)
            if((x > int(self.SCALE_X/2)) and (y < int(self.SCALE_Y/2))):
                self.CORNERS[1][0] = x+self.BORDER_BUFFER
                self.CORNERS[1][1] = y-self.BORDER_BUFFER
                self.Calibrate_Status = 2
        elif self.Calibrate_Status == 2:
            cv2.circle(cal_imag,(self.SCREEN_X-1,0), 50, (0,0,255), -1)
            cv2.circle(cal_imag,(self.SCREEN_X-16,15), 15, (255,0,0), -1)
            if((x < int(self.SCALE_X/2)) and (y < int(self.SCALE_Y/2))):
                self.CORNERS[0][0] = x-self.BORDER_BUFFER
                self.CORNERS[0][1] = y-self.BORDER_BUFFER
                self.Calibrate_Status = 3
        elif self.Calibrate_Status == 3:
            cv2.circle(cal_imag,(0,self.SCREEN_Y-1), 50, (0,0,255), -1)
            cv2.circle(cal_imag,(15,self.SCREEN_Y-16), 15, (255,0,0), -1)
            if((x > int(self.SCALE_X/2)) and (y > int(self.SCALE_Y/2))):
                self.CORNERS[3][0] = x+self.BORDER_BUFFER
                self.CORNERS[3][1] = y+self.BORDER_BUFFER
                self.Calibrate_Status = 4
        elif self.Calibrate_Status == 4:
            cv2.circle(cal_imag,(self.SCREEN_X-1,self.SCREEN_Y-1), 50, (0,0,255), -1)
            cv2.circle(cal_imag,(self.SCREEN_X-16,self.SCREEN_Y-16), 15, (255,0,0), -1)
            if((x < int(self.SCALE_X/2)) and (y > int(self.SCALE_Y/2))):
                self.CORNERS[2][0] = x-self.BORDER_BUFFER
                self.CORNERS[2][1] = y+self.BORDER_BUFFER
                self.Calibrate_Status = 0

        cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Calibrate", cal_imag)
        if self.Calibrate_Status == 0:
            self.SaveToJSON()
            cv2.destroyWindow("Calibrate")  
