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
            result = cv2.getWindowProperty(self.Name,cv2.WND_PROP_VISIBLE) > 0
        except:
            result = False
        return result
    
    #Convert hex to rgb
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        hex = [None] * 3
        counter = 0
        for i in range(0, lv, lv // 3):
            hex[counter] = int(value[i:i + lv // 3], 16)
            counter = counter + 1
        return hex



    #convert rgb to hex
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb

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
                colourRgb = OptionMenue.hex_to_rgb(self.Conf.SPRAY_COLOUR)
                colourRgb[0] = cv2.getTrackbarPos("Red",self.Name)
                colourRgb[1] = cv2.getTrackbarPos("Green",self.Name)
                colourRgb[2] = cv2.getTrackbarPos("Blue",self.Name)
                self.Conf.SPRAY_COLOUR = OptionMenue.rgb_to_hex((colourRgb[0], colourRgb[1], colourRgb[2]))
                GPU_ENABLED = cv2.getTrackbarPos("Enable GPU",self.Name)
                MAIL_ENABLED = cv2.getTrackbarPos("Enable Mail",self.Name)
                if self.Conf.BLUR < 1:
                    cv2.setTrackbarPos("Blur",self.Name, 1)
                    self.Conf.BLUR = 1
                if self.Conf.SCALE_X < 1:
                    cv2.setTrackbarPos("Scale X",self.Name, 1)
                    self.Conf.SCALE_X = 1
                if self.Conf.SCALE_Y < 1:
                    cv2.setTrackbarPos("Scale Y",self.Name, 1)
                    self.Conf.SCALE_Y = 1
                if GPU_ENABLED == 1:
                    self.Conf.GPU_ENABLED = True
                else:
                    self.Conf.GPU_ENABLED = False
                self.Conf.SaveToJSON()
                self.Conf.SCALE_FACTOR_X = self.Conf.SCREEN_X/self.Conf.SCALE_X
                self.Conf.SCALE_FACTOR_Y = self.Conf.SCREEN_Y/self.Conf.SCALE_Y

                self.Conf.MASK_LOWER = (self.Conf.MASK_COLORS[0],self.Conf.MASK_COLORS[2],self.Conf.MASK_COLORS[4], 0)
                self.Conf.MASK_UPPER = (self.Conf.MASK_COLORS[1],self.Conf.MASK_COLORS[3],self.Conf.MASK_COLORS[5], 0)
        except:
            return

    def Button_Reset(self, value):
        if value == 1 and self.start == False:
            self.Conf = self.Conf_Old.copy() # Restore conf
            colourRgb = OptionMenue.hex_to_rgb(self.Conf.SPRAY_COLOUR)
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
            cv2.setTrackbarPos("Red",self.Name, colourRgb[0])
            cv2.setTrackbarPos("Green",self.Name, colourRgb[1])
            cv2.setTrackbarPos("Blue",self.Name, colourRgb[2])
            if self.Conf.GPU_ENABLED == True:
                cv2.setTrackbarPos("Enable GPU",self.Name, 1)
            else:
                cv2.setTrackbarPos("Enable GPU",self.Name, 0)
            if self.Conf.MAIL_ENABLED == True:
                cv2.setTrackbarPos("Enable Mail",self.Name, 1)
            else:
                cv2.setTrackbarPos("Enable Mail",self.Name, 0)
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
            colourRgb = OptionMenue.hex_to_rgb(self.Conf.SPRAY_COLOUR)
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
            cv2.createTrackbar("Red",self.Name,colourRgb[0],255,self.setTrackbarPos)
            cv2.createTrackbar("Green",self.Name,colourRgb[1],255,self.setTrackbarPos)
            cv2.createTrackbar("Blue",self.Name,colourRgb[2],255,self.setTrackbarPos)
            self.Conf.SPRAY_COLOUR = OptionMenue.rgb_to_hex((colourRgb[0], colourRgb[1], colourRgb[2]))
            if self.Conf.GPU_ENABLED == True:
                cv2.createTrackbar("Enable GPU",self.Name,1,1, self.setTrackbarPos)
            else:
                cv2.createTrackbar("Enable GPU",self.Name,0,1, self.setTrackbarPos)
            if self.Conf.MAIL_ENABLED == True:
                cv2.createTrackbar("Enable Mail",self.Name,1,1, self.setTrackbarPos)
            else:
                cv2.createTrackbar("Enable Mail",self.Name,0,1, self.setTrackbarPos)
            cv2.createTrackbar("Reset",self.Name,0,1, self.Button_Reset)
            self.start = False
            
    def Close(self):
        cv2.destroyWindow(self.Name)  