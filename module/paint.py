import io
import math                  # For calculating distance
import random                # Random scattering
from tkinter import Tk, Canvas, PhotoImage
from PIL import Image, ImageDraw

try:
    from PIL import ImageTk
    HAS_IMAGETK = True
except ImportError:
    HAS_IMAGETK = False

class Paint:
    Name = "PAINT SCREEN"
    SPRAY_COLOUR = "#00FF00"
    
    def __init__(self, spray_color="#00FF00", visible=True):
        self.SPRAY_COLOUR = spray_color
        self.spread_x = 2
        self.spread_y = 2
        self.distance_multiplier = 2

        # Backward compatibility aliases
        self.xVerteilung = self.spread_x
        self.yVerteilung = self.spread_y
        self.abstandMultiplier = self.distance_multiplier
        
        # Screen init
        self.tkScreen = Tk()
        self.tkScreen.attributes('-fullscreen', True)
        self.tkScreen.title(self.Name)
        
        self.width = self.tkScreen.winfo_screenwidth()
        self.height = self.tkScreen.winfo_screenheight()
        if self.width <= 0:
            self.width = 1920
        if self.height <= 0:
            self.height = 1080

        self.canvas = Canvas(self.tkScreen, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # In-memory drawing buffer to prevent creating tens of thousands of Tkinter canvas objects
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.dirty = False

        self.photo = self._create_photo_image()
        self.canvas_image_item = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        if visible:
            self.Show()
        else:
            self.Hide()

    def _create_photo_image(self):
        if HAS_IMAGETK:
            return ImageTk.PhotoImage(self.image)
        buf = io.BytesIO()
        self.image.save(buf, format="PPM")
        return PhotoImage(data=buf.getvalue())
    
    def Hide(self):
        self.tkScreen.withdraw()
        self.Screen_Update()
        
    def Show(self):
        self.tkScreen.deiconify()
        self.Screen_Update()
        
    def End(self):
        try:
            self.tkScreen.destroy()
        except Exception:
            pass

    def clear(self):
        self.draw.rectangle([0, 0, self.width, self.height], fill="white")
        self.dirty = True
        self.Screen_Update()
    
    def get_distance(self, fromX, fromY, toX, toY):
        return round(math.sqrt((toX - fromX)**2 + (toY - fromY)**2) * self.distance_multiplier)

    def getAbstand(self, fromX, fromY, toX, toY):
        return self.get_distance(fromX, fromY, toX, toY)

    def get_spread(self, blobSize):
        val = int((blobSize / 20) * (blobSize / 20))
        return val, val

    def getVerteilung(self, blobSize):
        return self.get_spread(blobSize)

    def createGrafittiLine(self, fromX, fromY, toX, toY, blobSize):
        distance = self.get_distance(fromX, fromY, toX, toY)
        spread_x, spread_y = self.get_spread(blobSize)
        for _ in range(distance):
            factor = random.random()
            newX = fromX + factor * (toX - fromX) + random.randint(-spread_x, spread_x)
            newY = fromY + factor * (toY - fromY) + random.randint(-spread_y, spread_y)
            self.draw.ellipse([newX, newY, newX + 2, newY + 2], fill=self.SPRAY_COLOUR)
        self.dirty = True

    def createGrafittiLineBigger(self, fromX, fromY, toX, toY, blobSize):
        distance = self.get_distance(fromX, fromY, toX, toY) * 2
        spread_x, spread_y = self.get_spread(blobSize)
        spread_x *= 6
        spread_y *= 6
        for _ in range(distance):
            factor = random.random()
            newX = fromX + factor * (toX - fromX) + random.randint(-spread_x, spread_x)
            newY = fromY + factor * (toY - fromY) + random.randint(-spread_y, spread_y)
            self.draw.ellipse([newX, newY, newX + 2, newY + 2], fill=self.SPRAY_COLOUR)
        self.dirty = True
        
    def Screen_Update(self):
        if self.dirty:
            self.photo = self._create_photo_image()
            self.canvas.itemconfig(self.canvas_image_item, image=self.photo)
            self.dirty = False
        try:
            self.tkScreen.update()
        except Exception:
            pass