import math                  # For calculating sqrt
import random                # Random number
from tkinter import *        # Drawing
# from PIL import Image, ImageTk 

# Paint
class Paint:
    tkScreen = None
    xVerteilung = 2
    yVerteilung = 2
    abstandMultiplier = 2 # Mehr Punkte auf der Linie
    Name = "PAINT SCREEN"
    SPRAY_COLOUR = "#00FF00"
    
    def __init__(self, spray_color="#00FF00", visible=True):
        self.SPRAY_COLOUR = spray_color
        # Screen init
        self.tkScreen = Tk()
        self.tkScreen.attributes('-fullscreen' , True)
        self.tkScreen.title(self.Name)
        self.canvas = Canvas(self.tkScreen, width=self.tkScreen.winfo_screenwidth(), height=self.tkScreen.winfo_screenheight(), bg="white")
        self.canvas.pack()
        if visible:
            self.Show()
        else:
            self.Hide()
    
    def Hide(self):
        self.tkScreen.withdraw() # Hide the screen
        self.Screen_Update()
        
    def Show(self):
        self.tkScreen.deiconify() # Show the screen
        self.Screen_Update()
        
    def End(self):
        self.tkScreen.destroy()
    
    # fromX + g * (toX - fromX) => newX (0 <= g <= 1)
    # fromY + g * (toY - fromY) => newY (0 <= g <= 1)
    def getAbstand(self, fromX, fromY, toX, toY):
        return round((math.sqrt((toX - fromX)**2 + (toY - fromY)**2)) * self.abstandMultiplier)

    def getVerteilung(self, blobSize):
        x = int((blobSize/20) * (blobSize/20)) # 30 => 3 * 3 => 9
        y = int((blobSize/20) * (blobSize/20)) # 60 => 6 * 6 => 36 
        return x, y

    def createGrafittiLine(self, fromX, fromY, toX, toY, blobSize):
        abstandFromTo = self.getAbstand(fromX, fromY, toX, toY) # Anzahl der Punkte zum erstellen
        currXVerteilung, currYVerteilung = self.getVerteilung(blobSize)
        for e in range(0, abstandFromTo):
            randG0To1 = random.random()
            newX = fromX + randG0To1 * (toX - fromX)
            newY = fromY + randG0To1 * (toY - fromY)
            newX = random.randint(-currXVerteilung, currXVerteilung) + newX
            newY = random.randint(-currYVerteilung, currYVerteilung) + newY
            # print("Abstand", abstandFromTo, "RandG", str(randG0To1), "NewX", str(newX), "NewY", str(newY))
            self.canvas.create_oval(newX, newY, newX+2, newY+2, fill=self.SPRAY_COLOUR, outline=self.SPRAY_COLOUR)
        # self.tkScreen.update()
        # canvas.create_line(fromX, from.Y, toX, toY, fill="red", width=5)

    def createGrafittiLineBigger(self, fromX, fromY, toX, toY, blobSize):
        abstandFromTo = self.getAbstand(fromX, fromY, toX, toY) * 2 # Anzahl der Punkte zum erstellen
        currXVerteilung, currYVerteilung = self.getVerteilung(blobSize) 
        currXVerteilung = currXVerteilung * 6 # Größere Verteilung
        currYVerteilung = currYVerteilung * 6
        for e in range(0, abstandFromTo):
            randG0To1 = random.random()
            newX = fromX + randG0To1 * (toX - fromX)
            newY = fromY + randG0To1 * (toY - fromY)
            newX = random.randint(-currXVerteilung, currXVerteilung) + newX
            newY = random.randint(-currYVerteilung, currYVerteilung) + newY
            # print("Abstand", abstandFromTo, "RandG", str(randG0To1), "NewX", str(newX), "NewY", str(newY))
            self.canvas.create_oval(newX, newY, newX+2, newY+2, fill=self.SPRAY_COLOUR, outline=self.SPRAY_COLOUR)
        # self.tkScreen.update()
        # canvas.create_line(fromX, from.Y, toX, toY, fill="red", width=5)
        
    def Screen_Update(self):
        self.tkScreen.update()
        
    # def create_rectangle(self, x,y,a,b,**options):
    #     images=[]
    #     if 'alpha' in options:
    #         # Calculate the alpha transparency for every color(RGB)
    #         alpha = int(options.pop('alpha') * 255)
    #         # Use the fill variable to fill the shape with transparent color
    #         fill = options.pop('fill')
    #         fill = self.tkScreen.winfo_rgb(fill) + (alpha,)
    #         image = Image.new('RGBA', (a-x, b-y), fill)
    #         images.append(ImageTk.PhotoImage(image))
    #         self.canvas.create_image(x, y, image=images[-1], anchor='nw')
    #         self.canvas.create_rectangle(x, y,a,b, **options)
    
    # def Draw(self, x, y, size):
    #     x = int(x)
    #     y = int(y)
    #     # self.canvas.create_oval(x, y, x+(size*2), y+(size*2), fill=self.SPRAY_COLOUR, outline=self.SPRAY_COLOUR)
    #     # self.create_rectangle(x, y, int(x+(size*2)), int(y+(size*2)), fill="blue", alpha=.3)
    #     self.create_rectangle(50, 110,300,280, fill=self.SPRAY_COLOUR, alpha=.3)
        
    #     self.Screen_Update()