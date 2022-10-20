import pygame                # Sound
from os.path import exists   # If file exists

class Sound:
    def __init__(self, file):
        #Sound
        pygame.mixer.init()
        if not exists(file):
            print("There is no sound file named {}!", file)
        else:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.pause()
            
    def play(self):
        pygame.mixer.music.unpause()
        
    def stop(self):
        pygame.mixer.music.pause()