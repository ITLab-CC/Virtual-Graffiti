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
from tkinter import simpledialog, messagebox

def _to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes")
    return bool(val)

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
    MASK_LOWER = (MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4], 0)
    MASK_UPPER = (MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5], 0)
    Calibrate_Status = 0

    def __init__(self):
        # Ensure mutable structures are per-instance
        self.CALIBRATION_POINTS = [p.copy() for p in Config.CALIBRATION_POINTS]
        self.MASK_COLORS = list(Config.MASK_COLORS)
        self.MASK_LOWER = (self.MASK_COLORS[0], self.MASK_COLORS[2], self.MASK_COLORS[4], 0)
        self.MASK_UPPER = (self.MASK_COLORS[1], self.MASK_COLORS[3], self.MASK_COLORS[5], 0)
    
    def autodetect(self):
        #Get screen size
        try:
            sct=mss.mss()
            self.SCREEN_X=int(sct.monitors[1]['width'])
            self.SCREEN_Y=int(sct.monitors[1]['height'])
        except:
            self.SCREEN_X=1920
            self.SCREEN_Y=1080
        
        #find camera
        devices = find_camera()
        if len(devices) > 0:
            self.CAMERA_SRC=devices[0]
            
        # Find best algorithm for cv2
        algo = find_cv2_algorithm(0.5)
        if len(algo) > 0 and algo[0][2] > 0:
            self.CV2_ALGORITHM_NUMBER=algo[0][0]

    def copy_from(self, other):
        for attr, value in other.__dict__.items():
            if isinstance(value, list):
                setattr(self, attr, [item.copy() if isinstance(item, list) else item for item in value])
            else:
                setattr(self, attr, value)
            
    def copy(self, other=None):
        target = Config() if other is None else other
        target.copy_from(self)
        target.DEBUG = self.DEBUG
        target.GPU_ENABLED = self.GPU_ENABLED
        target.PAINT_ENABLED = self.PAINT_ENABLED
        target.SCREEN_X = self.SCREEN_X
        target.SCREEN_Y = self.SCREEN_Y
        target.CAMERA_X = self.CAMERA_X
        target.CAMERA_Y = self.CAMERA_Y
        target.SCALE_X = self.SCALE_X
        target.SCALE_Y = self.SCALE_Y
        target.SCALE_FACTOR_X = self.SCALE_FACTOR_X
        target.SCALE_FACTOR_Y = self.SCALE_FACTOR_Y
        target.CAMERA_SRC = self.CAMERA_SRC
        target.CAMERA_FPS = self.CAMERA_FPS
        target.CV2_ALGORITHM_NUMBER = self.CV2_ALGORITHM_NUMBER
        target.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE
        target.CALIBRATION_POINTS = [p.copy() for p in self.CALIBRATION_POINTS]
        target.MASK_COLORS = list(self.MASK_COLORS)
        target.BLUR = self.BLUR
        target.BORDER_BUFFER = self.BORDER_BUFFER
        target.SPRAY_COLOUR = self.SPRAY_COLOUR
        target.MASK_LOWER = (self.MASK_COLORS[0], self.MASK_COLORS[2], self.MASK_COLORS[4], 0)
        target.MASK_UPPER = (self.MASK_COLORS[1], self.MASK_COLORS[3], self.MASK_COLORS[5], 0)
        target.Calibrate_Status = self.Calibrate_Status
        return target

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
            json.dump(data, outfile, indent=4)

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
                cfg = data['config']
                self.DEBUG = _to_bool(cfg.get('DEBUG', self.DEBUG))
                self.GPU_ENABLED = _to_bool(cfg.get('GPU_ENABLED', self.GPU_ENABLED))
                self.PAINT_ENABLED = _to_bool(cfg.get('PAINT_ENABLED', self.PAINT_ENABLED))
                self.SCREEN_X = cfg.get('SCREEN_X', self.SCREEN_X)
                self.SCREEN_Y = cfg.get('SCREEN_Y', self.SCREEN_Y)
                self.CAMERA_X = cfg.get('CAMERA_X', self.CAMERA_X)
                self.CAMERA_Y = cfg.get('CAMERA_Y', self.CAMERA_Y)
                self.SCALE_X = cfg.get('SCALE_X', self.SCALE_X)
                self.SCALE_Y = cfg.get('SCALE_Y', self.SCALE_Y)
                self.CAMERA_SRC = cfg.get('CAMERA_SRC', self.CAMERA_SRC)
                self.CAMERA_FPS = cfg.get('CAMERA_FPS', self.CAMERA_FPS)
                self.CV2_ALGORITHM_NUMBER = cfg.get('CV2_ALGORITHM_NUMBER', self.CV2_ALGORITHM_NUMBER)
                self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = cfg.get('NUMBER_OF_CALIBRATION_POINTS_PER_LINE', self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE)
                self.CALIBRATION_POINTS = cfg.get('CALIBRATION_POINTS', self.CALIBRATION_POINTS)
                self.MASK_COLORS = cfg.get('MASK_COLORS', self.MASK_COLORS)
                self.BLUR = cfg.get('BLUR', self.BLUR)
                self.BORDER_BUFFER = cfg.get('BORDER_BUFFER', self.BORDER_BUFFER)
                self.SCALE_FACTOR_X = self.SCREEN_X / self.SCALE_X if self.SCALE_X else 1
                self.SCALE_FACTOR_Y = self.SCREEN_Y / self.SCALE_Y if self.SCALE_Y else 1
                self.SPRAY_COLOUR = cfg.get('SPRAY_COLOUR', self.SPRAY_COLOUR)
                self.MASK_LOWER = (self.MASK_COLORS[0], self.MASK_COLORS[2], self.MASK_COLORS[4], 0)
                self.MASK_UPPER = (self.MASK_COLORS[1], self.MASK_COLORS[3], self.MASK_COLORS[5], 0)
                
                expected_points = self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE * self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE
                if expected_points != len(self.CALIBRATION_POINTS):
                    print("The config has a wrong format. Resetting to defaults.")
                    self.copy_from(temp_old)
        except Exception as e:
            print(f"The config has a wrong format. Resetting to defaults. Error: {e}")
            self.copy_from(temp_old)
    
    #Calibration mode
    Calibrate_Status = 0
    # self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = 3 # must be >= 2
    def Calibrate_Points(self, orgx=-1, orgy=-1):
        x = orgx
        y = orgy
        if x == -1 and y == -1: # first call
            x = self.SCREEN_X
            y = self.SCREEN_Y
            root = tk.Tk()
            root.withdraw()
            while True:
                result = simpledialog.askstring("Input", "Enter a number between 2 and 10:", parent=root)
                if result is None:
                    break
                if not result.isdigit():
                    messagebox.showerror("Error", "Please enter a valid number.")
                    continue
                result = int(result)
                if result < 2 or result > 10:
                    messagebox.showerror("Error", "Please enter a number between 2 and 10.")
                    continue
                break
            root.destroy()
            if result is None:
                self.Calibrate_Status = 0
                return 
            
            self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE = result
            self.CALIBRATION_POINTS.clear()
            
        x = self.SCALE_X-x # mirror cordinate x

        cal_imag = np.zeros((self.SCREEN_Y,self.SCREEN_X,3), np.uint8)      #black background
        cal_imag.fill(255)
        
        vertical =  (self.Calibrate_Status - 1) % self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE # get index of vertical point
        horizontal = int((self.Calibrate_Status -1) / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) # round off to get index of horizontal point
        
        point_x = int(((self.SCREEN_X / (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1)) * horizontal)-1)
        point_y = int(((self.SCREEN_Y / (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1)) * vertical)-1)
        
        buffer_X = 0
        buffer_Y = 0
        
        shift_X = point_x
        if horizontal == 0:
            shift_X += 15
        elif horizontal == self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1:
            shift_X -= 15
        shift_Y = point_y
        if vertical == 0:
            shift_Y += 15
        elif vertical == self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE -1:
            shift_Y -= 15
        
        from_X = int(self.SCALE_X / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (horizontal)
        to_X = int(self.SCALE_X / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (horizontal + 1)
        from_Y = int(self.SCALE_Y / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (vertical)
        to_Y = int(self.SCALE_Y / self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE) * (vertical + 1)
                
                
        cv2.circle(cal_imag,(point_x-1,point_y-1), 50, (0,0,255), -1)
        cv2.circle(cal_imag,(shift_X,shift_Y), 15, (255,0,0), -1)
                
        cv2.namedWindow("Calibrate", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Calibrate",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Calibrate", cal_imag)
        
        if (x <= to_X) and (x >= from_X) and (y <= to_Y) and (y >= from_Y):
            self.CALIBRATION_POINTS.append([orgx,orgy])
            self.Calibrate_Status = self.Calibrate_Status + 1
            self.Calibrate_Points(-2, -2)    # Update the drawd points
            if(self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE > 6):
                messagebox.showinfo("Info", "Press enter to continue!") # wait for enter
           
        if self.Calibrate_Status > (self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE * self.NUMBER_OF_CALIBRATION_POINTS_PER_LINE):
            self.SaveToJSON()
            cv2.destroyWindow("Calibrate")  
            self.Calibrate_Status = 0