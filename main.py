import cv2                   # OpenCV
import time                  # Measure FPS
import sys

from module.config import Config
from module.optionmenue import OptionMenue
from module.imageprocessing import ImageProcessing
from module.paint import Paint
from module.sound import Sound
from module.mouse import Mouse


class VirtualGraffitiApp:
    def __init__(self):
        self.running = False
        self.conf = Config()
        self.conf.LoadFromJSON()
        self.conf_old = self.conf.copy()

        try:
            self.mouse = Mouse(self.conf.SCREEN_X, self.conf.SCREEN_Y)
        except Exception as e:
            print(f"Warning: Mouse/Tablet emulation unavailable: {e}")
            self.mouse = None

        self.options_menu = OptionMenue(self.conf, self.conf_old, "Options")
        self.paint = Paint(self.conf.SPRAY_COLOUR, self.conf.PAINT_ENABLED)
        self.sound = Sound(self.conf.SOUND_SPRAY_FILE)
        self.image_processing = ImageProcessing(self.conf, 1)

        self._init_paint_keys()

    def _init_paint_keys(self):
        def on_tk_key(event):
            self.handle_key(event.char.lower())

        for key in ('o', 'c', 'd', 'q', 'p', 'r'):
            self.paint.tkScreen.bind(key, on_tk_key)

    def handle_key(self, key):
        if not key:
            return
        if isinstance(key, int):
            key = chr(key & 0xFF).lower() if key != 255 else ""
        
        if key == 'q':
            self.stop()
        elif key == 'o':
            if self.options_menu.isOpen():
                self.options_menu.Close()
            else:
                self.options_menu.Open()
        elif key == 'c':
            if self.conf.Calibrate_Status == 0:
                self.conf.Calibrate_Status = 1
                self.conf.Calibrate_Points()
        elif key == 'd':
            self.conf.DEBUG = not self.conf.DEBUG
            if not self.conf.DEBUG:
                cv2.destroyAllWindows()
            self.conf.SaveToJSON()
        elif key == 'p':
            self.conf.PAINT_ENABLED = not self.conf.PAINT_ENABLED
            if self.conf.PAINT_ENABLED:
                self.paint.Show()
            else:
                self.paint.Hide()
            self.conf.SaveToJSON()
        elif key == 'r':
            if self.conf.PAINT_ENABLED:
                self.paint.clear()

    def stop(self):
        if not self.running and not hasattr(self, '_stopped'):
            return
        self.running = False
        self._stopped = True
        print("Shutting down cleanly...")
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()
        if hasattr(self, 'mouse') and self.mouse:
            try:
                self.mouse.release()
            except Exception:
                pass
        if hasattr(self, 'image_processing'):
            self.image_processing.end()
        if hasattr(self, 'paint'):
            self.paint.End()
        cv2.destroyAllWindows()
        print("Goodbye!")

    def run(self):
        self.running = True
        spraying = False
        last_pos = None
        last_time_input = None

        try:
            while self.running:
                # Check for OpenCV keyboard input
                k = cv2.waitKey(1)
                if k != -1:
                    self.handle_key(k)

                # Stop spraying if no input received for > 0.1s
                if last_time_input is not None and (time.time() - last_time_input > 0.1):
                    last_time_input = None
                    last_pos = None
                    if spraying:
                        if self.mouse:
                            self.mouse.release()
                        self.sound.stop()
                        spraying = False

                success, debug_img, coordinates, blob_sizes = self.image_processing.grap_coordinates()
                if not success:
                    if self.conf.PAINT_ENABLED:
                        self.paint.Screen_Update()
                    continue

                if self.conf.DEBUG and debug_img is not None:
                    cv2.imshow('Debug', debug_img)

                if coordinates:
                    last_time_input = time.time()
                    for idx, coord in enumerate(coordinates):
                        blob_size = blob_sizes[idx] if idx < len(blob_sizes) else 50
                        orgx = int(coord[0])
                        orgy = int(coord[1])
                        real_x = int(orgx * self.conf.SCALE_FACTOR_X)
                        real_y = int(orgy * self.conf.SCALE_FACTOR_Y)

                        if self.conf.Calibrate_Status > 0:
                            self.conf.Calibrate_Points(orgx, orgy)
                        elif not self.options_menu.isOpen():
                            # Bottom right corner toggles debug
                            if not spraying and (real_x >= self.conf.SCREEN_X - 100) and (real_y >= self.conf.SCREEN_Y - 100):
                                self.conf.DEBUG = True
                                self.conf.SaveToJSON()
                                continue

                            if self.conf.PAINT_ENABLED:
                                if last_pos is not None:
                                    self.paint.createGrafittiLine(last_pos[0], last_pos[1], real_x, real_y, blob_size)
                                    self.paint.createGrafittiLineBigger(last_pos[0], last_pos[1], real_x, real_y, blob_size)
                                last_pos = (real_x, real_y)
                            else:
                                if self.mouse:
                                    if not spraying:
                                        self.mouse.press(real_x, real_y)
                                    self.mouse.move(real_x, real_y)

                            if not spraying:
                                self.sound.play()
                                spraying = True

                    if self.conf.PAINT_ENABLED:
                        self.paint.Screen_Update()

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


if __name__ == "__main__":
    app = VirtualGraffitiApp()
    app.run()