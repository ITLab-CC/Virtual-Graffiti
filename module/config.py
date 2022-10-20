import cv2                   # OpenCV
import json                  # Read write config as json
import mss                   # Get the screen size
import platform              # Get host platform (MacOS/Windows/Linux)
from os.path import exists   # If file exists
import numpy as np           # Create arrays
from module.threadedcamera import find_camera
from module.threadedcamera import find_cv2_algorithm

class Config:
    DEBUG = True
    GPU_ENABLED = False
    PAINT_ENABLED = True
    CONFIG_FILE="config.conf"
    SOUND_SPRAY_FILE="sounds/spray.mp3"
    SCREEN_X=1920
    SCREEN_Y=1080
    CAMERA_X=1920
    CAMERA_Y=1080
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
    CAMERA_SRC=0
    CAMERA_FPS=60
    CV2_ALGORITHM_NUMBER=cv2.CAP_ANY
    
    # MASK_LOWER = np.array([MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4]])
    # MASK_UPPER= np.array([MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5]])
    MASK_LOWER = (MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4], 0)
    MASK_UPPER = (MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5], 0)
    
    # def <c(self):
    #     self.LoadFromJSON()
    
    def autodetect(self):
        #Get screen size
        try:
            sct=mss.mss()
            self.SCREEN_X=int(sct.monitors[1]['width'])
            self.SCREEN_Y=int(sct.monitors[1]['height'])
        except:
            self.SCREEN_X=1920
            self.SCREEN_Y=1080
            
        #Get camera size
        # ... TODO
        
        #find camera
        devices = find_camera()
        if not len(devices) == 0:
            self.CAMERA_SRC=devices[0]
            
        # Find best algorithm for cv2
        algo = find_cv2_algorithm(3)
        if algo[0][2] > 0:
            self.CV2_ALGORITHM_NUMBER=algo[0][0]
        
                
            
    def copy(self, other=None):
        if not(isinstance(other,Config)) or other==None:
            other = Config()
        else:
            other = self
        other.CORNERS=self.CORNERS.copy()
        other.MASK_COLORS=self.MASK_COLORS.copy()
        # other.MASK_LOWER=np.array([self.MASK_COLORS[0],self.MASK_COLORS[2],self.MASK_COLORS[4]])
        # other.MASK_UPPER=np.array([self.MASK_COLORS[1],self.MASK_COLORS[3],self.MASK_COLORS[5]])
        other.MASK_LOWER = (self.MASK_COLORS[0],self.MASK_COLORS[2],self.MASK_COLORS[4], 0)
        other.MASK_UPPER = (self.MASK_COLORS[1],self.MASK_COLORS[3],self.MASK_COLORS[5], 0)
        return other

    #Save vars to config.conf file
    def SaveToJSON(self):
        data = {
            'config' : {
                'DEBUG': self.DEBUG,
                'GPU_ENABLED': self.GPU_ENABLED,
                'PAINT_ENABLED' : self.PAINT_ENABLED,
                'SCREEN_X' : self.SCREEN_X,
                'SCREEN_Y' : self.SCREEN_Y,
                'CAMERA_X' : self.CAMERA_X,
                'CAMERA_Y' : self.CAMERA_Y,
                'SCALE_X' : self.SCALE_X,
                'SCALE_Y' : self.SCALE_Y,
                'CAMERA_SRC' : self.CAMERA_SRC,
                'CAMERA_FPS' : self.CAMERA_FPS,
                'CV2_ALGORITHM_NUMBER' : self.CV2_ALGORITHM_NUMBER,
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
            self.autodetect()
            self.SaveToJSON()
            return
        temp_old = self.copy()
        try:
            with open(self.CONFIG_FILE) as json_file:
                data = json.load(json_file)
                self.DEBUG = data['config']['DEBUG']
                self.GPU_ENABLED = data['config']['GPU_ENABLED']
                self.PAINT_ENABLED = data['config']['PAINT_ENABLED']
                if self.DEBUG == "true":
                    self.DEBUG = True
                if self.DEBUG == "false":
                    self.DEBUG = False
                if self.PAINT_ENABLED == "true":
                    self.PAINT_ENABLED = True
                if self.PAINT_ENABLED == "false":
                    self.PAINT_ENABLED = False
                self.SCREEN_X = data['config']['SCREEN_X']
                self.SCREEN_Y = data['config']['SCREEN_Y']
                self.CAMERA_X = data['config']['CAMERA_X']
                self.CAMERA_Y = data['config']['CAMERA_Y']
                self.SCALE_X = data['config']['SCALE_X']
                self.SCALE_Y = data['config']['SCALE_Y']
                self.CAMERA_SRC = data['config']['CAMERA_SRC']
                self.CAMERA_FPS = data['config']['CAMERA_FPS']
                self.CV2_ALGORITHM_NUMBER = data['config']['CV2_ALGORITHM_NUMBER']
                self.CORNERS = data['config']['CORNERS']
                self.MASK_COLORS = data['config']['MASK_COLORS']
                self.BLUR = data['config']['BLUR']
                self.BORDER_BUFFER = data['config']['BORDER_BUFFER']
                self.SCALE_FACTOR_X = self.SCREEN_X/self.SCALE_X
                self.SCALE_FACTOR_Y = self.SCREEN_Y/self.SCALE_Y
                self.SPRAY_COLOUR = data['config']['SPRAY_COLOUR']
                
                # self.MASK_LOWER=np.array([self.MASK_COLORS[0],self.MASK_COLORS[2],self.MASK_COLORS[4]])
                # self.MASK_UPPER=np.array([self.MASK_COLORS[1],self.MASK_COLORS[3],self.MASK_COLORS[5]])
                self.MASK_LOWER = (self.MASK_COLORS[0],self.MASK_COLORS[2],self.MASK_COLORS[4], 0)
                self.MASK_UPPER = (self.MASK_COLORS[1],self.MASK_COLORS[3],self.MASK_COLORS[5], 0)
        except Exception as e:
            print("The config has a wrong format. Delete the file and a new one will be generated. Error: {}" .format(e))
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
