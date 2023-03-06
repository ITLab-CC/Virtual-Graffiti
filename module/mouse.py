# https://gitlab.freedesktop.org/libevdev/python-libevdev/-/blob/master/examples/fake-tablet.py
# #!/usr/bin/env python3
#
# Fake tablet emulator

import sys
import libevdev
from libevdev import InputEvent, InputAbsInfo
import time

class Mouse:
    def __init__(self, screen_x, screen_y):
        self.dev = libevdev.Device()
        self.dev.name = "Wacom Cintiq Pro 16 Pen"
        self.dev.id = {'bustype': 0x3,
                'vendor': 0x56a,
                'product': 0x350,
                'version': 0xb}
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_RUBBER)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_BRUSH)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_PENCIL)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_AIRBRUSH)
        self.dev.enable(libevdev.EV_KEY.BTN_TOUCH)
        self.dev.enable(libevdev.EV_KEY.BTN_STYLUS)
        self.dev.enable(libevdev.EV_KEY.BTN_STYLUS2)
        self.dev.enable(libevdev.EV_KEY.BTN_STYLUS3)
        self.dev.enable(libevdev.EV_MSC.MSC_SERIAL)
        self.dev.enable(libevdev.INPUT_PROP_DIRECT)

        # a = InputAbsInfo(minimum=0, maximum=69920, resolution=200)
        # self.dev.enable(libevdev.EV_ABS.ABS_X, data=a)
        # a = InputAbsInfo(minimum=0, maximum=39980, resolution=200)
        # self.dev.enable(libevdev.EV_ABS.ABS_Y, data=a)
        a = InputAbsInfo(minimum=0, maximum=screen_x, resolution=100)
        self.dev.enable(libevdev.EV_ABS.ABS_X, data=a)
        a = InputAbsInfo(minimum=0, maximum=screen_y, resolution=100)
        self.dev.enable(libevdev.EV_ABS.ABS_Y, data=a)
        a = InputAbsInfo(minimum=-900, maximum=899, resolution=287)
        self.dev.enable(libevdev.EV_ABS.ABS_Z, data=a)
        a = InputAbsInfo(minimum=0, maximum=2047)
        self.dev.enable(libevdev.EV_ABS.ABS_WHEEL, data=a)
        a = InputAbsInfo(minimum=0, maximum=8196)
        self.dev.enable(libevdev.EV_ABS.ABS_PRESSURE, data=a)
        a = InputAbsInfo(minimum=0, maximum=8191)
        self.dev.enable(libevdev.EV_ABS.ABS_DISTANCE, data=a)
        a = InputAbsInfo(minimum=-64, maximum=63, resolution=57)
        self.dev.enable(libevdev.EV_ABS.ABS_TILT_X, data=a)
        self.dev.enable(libevdev.EV_ABS.ABS_TILT_Y, data=a)
        a = InputAbsInfo(minimum=0, maximum=0)
        self.dev.enable(libevdev.EV_ABS.ABS_MISC, data=a)
        
        self.uinput = self.dev.create_uinput_device()

        # try:
        #     uinput = self.dev.create_uinput_device()
        #     print("New device at {} ({})".format(uinput.devnode, uinput.syspath))

        #     # Sleep for a bit so udev, libinput, Xorg, Wayland, ... all have had
        #     # a chance to see the device and initialize it. Otherwise the event
        #     # will be sent by the kernel but nothing is ready to listen to the
        #     # device yet.
        #     time.sleep(1)

        #     x, y = 3000, 5000

        #     events = self.press(x, y)
        #     uinput.send_events(events)
        #     time.sleep(0.012)

        #     for _ in range(5):
        #         x += 1000
        #         y += 1000
        #         events = self.move(x, y)
        #         uinput.send_events(events)
        #         time.sleep(0.012)

        #     events = self.release()
        #     uinput.send_events(events)
        #     time.sleep(0.012)
        # except OSError as e:
        #     print(e)
            
    def press(self, x, y, tilt=(0, 0), pressure=8190    , distance=0, screen=0):
        z = 0
        print("Press")
        self.uinput.send_events([
            InputEvent(libevdev.EV_ABS.ABS_X, x),
            InputEvent(libevdev.EV_ABS.ABS_Y, y),
            InputEvent(libevdev.EV_ABS.ABS_Z, z),
            # Note: wheel for pen/eraser must be 0
            InputEvent(libevdev.EV_ABS.ABS_WHEEL, 0),
            InputEvent(libevdev.EV_ABS.ABS_PRESSURE, pressure),
            InputEvent(libevdev.EV_ABS.ABS_DISTANCE, distance),
            InputEvent(libevdev.EV_ABS.ABS_TILT_X, tilt[0]),
            InputEvent(libevdev.EV_ABS.ABS_TILT_Y, tilt[1]),
            InputEvent(libevdev.EV_ABS.ABS_MISC, 2083),
            InputEvent(libevdev.EV_MSC.MSC_SERIAL, 297797542),
            # Change to BTN_TOOL_RUBBER for the eraser end
            InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN, 1),
            InputEvent(libevdev.EV_SYN.SYN_REPORT, 0),
        ])

    lastx = 0
    lasty = 0
    lastpressure = 0
    
    def release(self):
        print("release2")
        self.uinput.send_events([
            InputEvent(libevdev.EV_ABS.ABS_X, 0),
            InputEvent(libevdev.EV_ABS.ABS_Y, 0),
            InputEvent(libevdev.EV_ABS.ABS_Z, 0),
            InputEvent(libevdev.EV_ABS.ABS_WHEEL, 0),
            InputEvent(libevdev.EV_ABS.ABS_PRESSURE, 0),
            InputEvent(libevdev.EV_ABS.ABS_DISTANCE, 0),
            InputEvent(libevdev.EV_ABS.ABS_TILT_X, 0),
            InputEvent(libevdev.EV_ABS.ABS_TILT_Y, 0),
            InputEvent(libevdev.EV_ABS.ABS_MISC, 0),
            InputEvent(libevdev.EV_MSC.MSC_SERIAL, 297797542),
            InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN, 0),
            InputEvent(libevdev.EV_SYN.SYN_REPORT, 0),
        ])
        while self.lastpressure > 0:
            self.move(self.lastx, self.lasty, (0,0), 0, False)
            self.lastpressure = self.lastpressure - 1


    def move(self, x, y, tilt=(0, 0), pressure=8191, anti = True, distance=0):
        z = 0
        if anti:
            self.lastx = x
            self.lasty = y
            self.lastpressure = pressure
        self.uinput.send_events([
            InputEvent(libevdev.EV_ABS.ABS_X, x),
            InputEvent(libevdev.EV_ABS.ABS_Y, y),
            InputEvent(libevdev.EV_ABS.ABS_Z, z),
            InputEvent(libevdev.EV_ABS.ABS_WHEEL, 0),
            InputEvent(libevdev.EV_ABS.ABS_PRESSURE, pressure),
            InputEvent(libevdev.EV_ABS.ABS_DISTANCE, distance),
            InputEvent(libevdev.EV_ABS.ABS_TILT_X, tilt[0]),
            InputEvent(libevdev.EV_ABS.ABS_TILT_Y, tilt[1]),
            InputEvent(libevdev.EV_MSC.MSC_SERIAL, 297797542),
            InputEvent(libevdev.EV_SYN.SYN_REPORT, 0),
        ])