from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame                # Sound
from os.path import exists   # If file exists

class Sound:
    def __init__(self, file):
        self.enabled = False
        self.is_playing = False
        try:
            pygame.mixer.init()
            if not exists(file):
                print(f"There is no sound file named {file}!")
                return
            pygame.mixer.music.load(file)
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.pause()
            self.enabled = True
        except Exception as e:
            print(f"Sound initialization disabled or failed: {e}")

    def play(self):
        if self.enabled and not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self):
        if self.enabled and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False