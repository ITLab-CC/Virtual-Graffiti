import cv2                   # OpenCV
import numpy as np           # Create arrays

class OptionMenue:
    Name = "Options"
    
    def __init__(self, conf, conf_old, name = "Options"):
        self.Name = name
        self.Conf = conf
        self.Conf_Old = conf_old
    
    def isOpen(self):
        try:
            result = cv2.getWindowProperty("Options",cv2.WND_PROP_VISIBLE) > 0
        except:
            result = False
        return result
    #Options menu
    def setTrackbarPos(self, value):
        try:
            if self.start == False:
                self.Conf.SCALE_X = cv2.getTrackbarPos("Scale X",self.Name)
                self.Conf.SCALE_Y = cv2.getTrackbarPos("Scale Y",self.Name)
                self.Conf.MASK_COLORS[0] = cv2.getTrackbarPos("Hue Min",self.Name)
                self.Conf.MASK_COLORS[1] = cv2.getTrackbarPos("Hue Max",self.Name)
                self.Conf.MASK_COLORS[2] = cv2.getTrackbarPos("Sat Min",self.Name)
                self.Conf.MASK_COLORS[3] = cv2.getTrackbarPos("Sat Max",self.Name)
                self.Conf.MASK_COLORS[4] = cv2.getTrackbarPos("Val Min",self.Name)
                self.Conf.MASK_COLORS[5] = cv2.getTrackbarPos("Val Max",self.Name)
                self.Conf.BLUR = cv2.getTrackbarPos("Blur",self.Name)
                self.Conf.BORDER_BUFFER = cv2.getTrackbarPos("Boarder Buffer",self.Name)
                if self.Conf.BLUR < 1:
                    cv2.setTrackbarPos("Blur",self.Name, 1)
                    self.Conf.BLUR = 1
                if self.Conf.SCALE_X < 1:
                    cv2.setTrackbarPos("Scale X",self.Name, 1)
                    self.Conf.SCALE_X = 1
                if self.Conf.SCALE_Y < 1:
                    cv2.setTrackbarPos("Scale Y",self.Name, 1)
                    self.Conf.SCALE_Y = 1
                self.Conf.SaveToJSON()
                self.Conf.SCALE_FACTOR_X = self.Conf.SCREEN_X/self.Conf.SCALE_X
                self.Conf.SCALE_FACTOR_Y = self.Conf.SCREEN_Y/self.Conf.SCALE_Y
                
                self.Conf.MASK_LOWER=np.array([self.Conf.MASK_COLORS[0],self.Conf.MASK_COLORS[2],self.Conf.MASK_COLORS[4]])
                self.Conf.MASK_UPPER=np.array([self.Conf.MASK_COLORS[1],self.Conf.MASK_COLORS[3],self.Conf.MASK_COLORS[5]])
        except:
            return;

    def Button_Reset(self, value):
        if value == 1 and self.start == False:
            self.Conf = self.Conf_Old.copy() # Restore conf
            cv2.setTrackbarPos("Scale X",self.Name, self.Conf.SCALE_X)
            cv2.setTrackbarPos("Scale Y",self.Name, self.Conf.SCALE_Y)
            cv2.setTrackbarPos("Hue Min",self.Name, self.Conf.MASK_COLORS[0])
            cv2.setTrackbarPos("Hue Max",self.Name, self.Conf.MASK_COLORS[1])
            cv2.setTrackbarPos("Sat Min",self.Name, self.Conf.MASK_COLORS[2])
            cv2.setTrackbarPos("Sat Max",self.Name, self.Conf.MASK_COLORS[3])
            cv2.setTrackbarPos("Val Min",self.Name, self.Conf.MASK_COLORS[4])
            cv2.setTrackbarPos("Val Max",self.Name, self.Conf.MASK_COLORS[5])
            cv2.setTrackbarPos("Blur",self.Name, self.Conf.BLUR)
            cv2.setTrackbarPos("Boarder Buffer",self.Name, self.Conf.BORDER_BUFFER)
            cv2.setTrackbarPos("Reset",self.Name, 0)
            print("Reseted to: ", self.Conf.MASK_COLORS[0], self.Conf.MASK_COLORS[1], self.Conf.MASK_COLORS[2], self.Conf.MASK_COLORS[3], self.Conf.MASK_COLORS[4], self.Conf.MASK_COLORS[5], self.Conf.BLUR)

    # Open/Create options menu
    start = False
    def Open(self):
        if cv2.getWindowProperty(self.Name,cv2.WND_PROP_VISIBLE) <= 0:
            self.start = True
            self.Conf_Old = self.Conf.copy() # Backup conf
            cv2.namedWindow(self.Name)
            cv2.resizeWindow(self.Name,300,600)
            cv2.createTrackbar("Scale X",self.Name,self.Conf.SCALE_X,self.Conf.CAMERA_X, self.setTrackbarPos)
            cv2.createTrackbar("Scale Y",self.Name,self.Conf.SCALE_Y,self.Conf.CAMERA_Y, self.setTrackbarPos)
            cv2.createTrackbar("Hue Min",self.Name,self.Conf.MASK_COLORS[0],255, self.setTrackbarPos)
            cv2.createTrackbar("Hue Max",self.Name,self.Conf.MASK_COLORS[1],255, self.setTrackbarPos)
            cv2.createTrackbar("Sat Min",self.Name,self.Conf.MASK_COLORS[2],255, self.setTrackbarPos)
            cv2.createTrackbar("Sat Max",self.Name,self.Conf.MASK_COLORS[3],255, self.setTrackbarPos)
            cv2.createTrackbar("Val Min",self.Name,self.Conf.MASK_COLORS[4],255, self.setTrackbarPos)
            cv2.createTrackbar("Val Max",self.Name,self.Conf.MASK_COLORS[5],255, self.setTrackbarPos)
            cv2.createTrackbar("Blur",self.Name,self.Conf.BLUR,20, self.setTrackbarPos)
            cv2.createTrackbar("Boarder Buffer",self.Name, self.Conf.BORDER_BUFFER,50, self.setTrackbarPos)
            cv2.createTrackbar("Reset",self.Name,0,1, self.Button_Reset)
            self.start = False
            
    def Close(self):
        cv2.destroyWindow(self.Name)  