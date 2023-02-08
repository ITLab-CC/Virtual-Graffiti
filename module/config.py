import cv2                   # OpenCV
import json                  # Read write config as json
import mss                   # Get the screen size
import platform              # Get host platform (MacOS/Windows/Linux)
from os.path import exists   # If file exists
import numpy as np           # Create arrays
from module.threadedcamera import find_camera
from module.threadedcamera import find_cv2_algorithm
import time
import tkinter as tk
from tkinter import simpledialog

class Config:
    DEBUG = True
    GPU_ENABLED = False
    PAINT_ENABLED = False
    CONFIG_FILE="config.conf"
    SOUND_SPRAY_FILE="sounds/spray.mp3"
    SCREEN_X=1920
    SCREEN_Y=1080
    CAMERA_X=1920
    CAMERA_Y=1080
    SCALE_X=int(SCREEN_X/2)
    SCALE_Y=int(SCREEN_Y/2)
    SCALE_FACTOR_X = SCREEN_X/SCALE_X
    SCALE_FACTOR_Y = SCREEN_Y/SCALE_Y
    NUMBER_OF_CALIBRATION_POINTS_PER_LINE = 2
    CALIBRATION_POINTS=[[77, 7], [897, 25], [81, 501], [870, 517]]
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
        other.CALIBRATION_POINTS=self.CALIBRATION_POINTS.copy()
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
                'NUMBER_OF_CALIBRATION_POINTS_PER_LINE' : self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE,
                'CALIBRATION_POINTS' : self.CALIBRATION_POINTS,
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
                self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = data['config']['NUMBER_OF_CALIBRATION_POINTS_PER_LINE']
                self.CALIBRATION_POINTS = data['config']['CALIBRATION_POINTS']
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
                
                if self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE * self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE != len(self.CALIBRATION_POINTS):
                    print("The config has a wrong format. Delete the file and a new one will be generated.")
                    self = temp_old
        except Exception as e:
            print("The config has a wrong format. Delete the file and a new one will be generated. Error: {}" .format(e))
            self = temp_old
    
    #Calibration mode
    Calibrate_Status = 0
    # self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = 3 # must be >= 2
    def Calibrate_Points(self, x=-1, y=-1):
        if x < 0 or y < 0: # first call
            x = self.SCREEN_X
            y = self.SCREEN_Y
            root = tk.Tk()
            root.withdraw()
            while True:
                result = simpledialog.askstring("Input", "Geben Sie eine Zahl zwischen 2 und 10 ein:", parent=root)
                if result is None:
                    break
                if not result.isdigit():
                    tk.messagebox.showerror("Error", "Bitte geben Sie eine gültige Zahl ein.")
                    continue
                result = int(result)
                if result < 2 or result > 10:
                    tk.messagebox.showerror("Error", "Bitte geben Sie eine Zahl zwischen 2 und 10 ein.")
                    continue
                break
            root.destroy()
            if result is None:
                self.Calibrate_Status = 0
                return 
            
            self.Calibrate_Status = 1
            self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = result
            self.CALIBRATION_POINTS.clear()
            self.CALIBRATION_POINTSTION_POINTS = [] * self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE
            
        x = self.SCALE_X-x # mirror cordinate x

        cal_imag = np.zeros((self.SCREEN_Y,self.SCREEN_X,3), np.uint8)      #black background
        
        vertical =  (self.Calibrate_Status - 1) % self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE # get index of vertical point
        horizontal = int((self.Calibrate_Status -1) / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) # round off to get index of horizontal point
        
        point_x = int(((self.SCREEN_X / (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1)) * horizontal)-1)
        point_y = int(((self.SCREEN_Y / (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1)) * vertical)-1)
        
        buffer_X = 0
        buffer_Y = 0
        
        shift_X = point_x
        if horizontal == 0:
            shift_X += 15
            buffer_X -= self.BORDER_BUFFER
        elif horizontal == self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1:
            shift_X -= 15
            buffer_X += self.BORDER_BUFFER
        shift_Y = point_y
        if vertical == 0:
            shift_Y += 15
            buffer_Y -= self.BORDER_BUFFER
        elif vertical == self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1:
            shift_Y -= 15
            buffer_Y += self.BORDER_BUFFER
        
        cv2.circle(cal_imag,(point_x-1,point_y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(shift_X,shift_Y), 15, (255,0,0), -1)
        
        from_X = int(self.SCALE_X / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (horizontal)
        to_X = int(self.SCALE_X / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (horizontal + 1)
        from_Y = int(self.SCALE_Y / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (vertical)
        to_Y = int(self.SCALE_Y / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (vertical + 1)
        
        if (x <= to_X) and (x >= from_X) and (y <= to_Y) and (y >= from_Y):
            self.CALIBRATION_POINTS.append([x+buffer_X,y+buffer_Y])
            # self.CALIBRATION_POINTS[self.Calibrate_Status-1][0] = x+buffer_X
            # self.CALIBRATION_POINTS[self.Calibrate_Status-1][1] = y+buffer_Y
            self.Calibrate_Status = self.Calibrate_Status + 1
                
        cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Calibrate", cal_imag)
        if self.Calibrate_Status > (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE * self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE):
            self.SaveToJSON()
            cv2.destroyWindow("Calibrate")  
