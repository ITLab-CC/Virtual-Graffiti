import libevdev

class Mouse:
    
    def __init__(self):
        self.dev = libevdev.Device()
        self.dev.name = "Tablet alone"
        # Say that the device will send "absolute" values
        self.dev.enable(libevdev.INPUT_PROP_DIRECT)
        # Say that we are using the pen (not the erasor), and should be set to 1 when we are at proximity to the device.
        # See http://www.infradead.org/~mchehab/kernel_docs_pdf/linux-input.pdf page 9 (=13) and guidelines page 12 (=16), or the https://github.com/linuxwacom/input-wacom/blob/master/4.5/wacom_w8001.c (rdy=proximity)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
        self.dev.enable(libevdev.EV_KEY.BTN_TOOL_RUBBER)
        # Click
        self.dev.enable(libevdev.EV_KEY.BTN_TOUCH)
        # Press button 1 on pen
        self.dev.enable(libevdev.EV_KEY.BTN_STYLUS)
        # Press button 2 on pen, see great doc
        self.dev.enable(libevdev.EV_KEY.BTN_STYLUS2)
        # Send absolute X coordinate
        self.dev.enable(libevdev.EV_ABS.ABS_X,
                libevdev.InputAbsInfo(minimum=0, maximum=1920, resolution=100))
        # Send absolute Y coordinate
        self.dev.enable(libevdev.EV_ABS.ABS_Y,
                libevdev.InputAbsInfo(minimum=0, maximum=1080, resolution=100))
        # Send absolute pressure
        self.dev.enable(libevdev.EV_ABS.ABS_PRESSURE,
                libevdev.InputAbsInfo(minimum=0, maximum=8191))    
                
        # Use to confirm that we finished to send the informations
        # (to be sent after every burst of information, otherwise
        # the kernel does not proceed the information)
        self.dev.enable(libevdev.EV_SYN.SYN_REPORT)
        # Report buffer overflow
        self.dev.enable(libevdev.EV_SYN.SYN_DROPPED)
        self.uinput = self.dev.create_uinput_device()
        self.uinput.send_events([
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=0),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=1),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
        ])
        # Says that the pen it out of range of the tablet. Useful
        # to make sure you can move your mouse, and to avoid
        # strange things during the first draw.
        self.uinput.send_events([
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=0),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=0),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
        ])
            
    
    def move(self, x, y, pressure, sizeMax, sizeMin):
        if (pressure > 80):
            pressure = 80
        if (pressure < 40):
            pressure = 40
        pressure = (sizeMin + sizeMax) - pressure        # invert min and max == (min + max) - wert
        sizeMax -= sizeMin
        pressure -= sizeMax
        factor = 8191 / sizeMax
        # if pressure < 30:
        #     pressure = 30
        # self.dev.enable(libevdev.EV_ABS.ABS_PRESSURE,
        #         libevdev.InputAbsInfo(minimum=0, maximum=8191)) 
        # print(pressure)
        print()
        self.uinput.send_events([
            libevdev.InputEvent(libevdev.EV_ABS.ABS_X,
                                value=x),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_Y,
                                value=y),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE,
                                value= int(pressure * factor)),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=1),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS,
                                value=0),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_STYLUS2,
                                value=0),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=1),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
            ])
        
    def press(self, x, y):
        # print("Press!")
        self.uinput.send_events([
            # Pen close to device
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=1),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=1),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
        ])       

    def release(self):
        print("Release click.")
        self.uinput.send_events([
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=0),
            # Pen outside of the position
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=0),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
        ])