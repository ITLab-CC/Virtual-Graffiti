from curses import termattrs
from pymouse import PyMouse

class Mouse:
    
    def __init__(self):
        self.mouse = PyMouse()
        
    def move(self, x, y):
        self.mouse.move(x, y)
        
    def press(self, x, y):
        self.mouse.press(x, y)
        
    def release(self, x, y):
        self.mouse.release(x, y)