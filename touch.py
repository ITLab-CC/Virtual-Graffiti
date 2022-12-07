#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import libevdev
import time
## Some doc needed for this project
# http://www.infradead.org/~mchehab/kernel_docs_pdf/linux-input.pdf

## Some code to get inspiration from
# https://github.com/linuxwacom/input-wacom/blob/master/4.5/wacom_w8001.c

## Some doc to read at some point in my life:
# https://lwn.net/Kernel/LDD3/
# https://www.kernel.org/doc/html/v4.11/driver-api/index.html

def main(args):
    dev = libevdev.Device()
    dev.name = "Tablet alone"
    ### NB: all the following information needs to be enabled
    ### in order to recognize the device as a tablet.
    # Say that the device will send "absolute" values
    dev.enable(libevdev.INPUT_PROP_DIRECT)
    # Say that we are using the pen (not the erasor), and should be set to 1 when we are at proximity to the device.
    # See http://www.infradead.org/~mchehab/kernel_docs_pdf/linux-input.pdf page 9 (=13) and guidelines page 12 (=16), or the https://github.com/linuxwacom/input-wacom/blob/master/4.5/wacom_w8001.c (rdy=proximity)
    dev.enable(libevdev.EV_KEY.BTN_TOOL_PEN)
    dev.enable(libevdev.EV_KEY.BTN_TOOL_RUBBER)
    # Click
    dev.enable(libevdev.EV_KEY.BTN_TOUCH)
    # Press button 1 on pen
    dev.enable(libevdev.EV_KEY.BTN_STYLUS)
    # Press button 2 on pen, see great doc
    dev.enable(libevdev.EV_KEY.BTN_STYLUS2)
    # Send absolute X coordinate
    dev.enable(libevdev.EV_ABS.ABS_X,
               libevdev.InputAbsInfo(minimum=0, maximum=1920, resolution=100))
    # Send absolute Y coordinate
    dev.enable(libevdev.EV_ABS.ABS_Y,
               libevdev.InputAbsInfo(minimum=0, maximum=1080, resolution=100))
    # Send absolute pressure
    dev.enable(libevdev.EV_ABS.ABS_PRESSURE,
               libevdev.InputAbsInfo(minimum=0, maximum=8191))
    # Use to confirm that we finished to send the informations
    # (to be sent after every burst of information, otherwise
    # the kernel does not proceed the information)
    dev.enable(libevdev.EV_SYN.SYN_REPORT)
    # Report buffer overflow
    dev.enable(libevdev.EV_SYN.SYN_DROPPED)
    try:
        uinput = dev.create_uinput_device()
        print("New device at {} ({})".format(uinput.devnode, uinput.syspath))
        # Sleep for a bit so udev, libinput, Xorg, Wayland, ...
        # all have had a chance to see the device and initialize
        # it. Otherwise the event will be sent by the kernel but
        # nothing is ready to listen to the device yet. And it
        # will never be detected in the futur ;-)
        time.sleep(1) 
        # Reports that the PEN is close to the surface
        # Important to make sure xinput can detect (and list)
        # the pen. Otherwise, it won't write anything in gimp.
        uinput.send_events([
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
        uinput.send_events([
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                value=0),
            libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                value=0),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                value=0),
        ])
        print("Waiting 30s to let you:")
        print("1) open Gimp")
        print("2) Go to 'Edit/Input device' and configure the device 'Tablet alone' to 'Screen'.")
        print("3) Save and close the pop up")
        print("4) Create a new file (Ctrl-N)")
        print("5) Zoom and press 'tab' to have a drawing surface coverint most of the screen.")
        print("6) Switch to brush using 'p' key.")
        time.sleep(3)

        pc = 0
        direc = +1
        already_pressed_one = False
        for i in range(250):
            pc_ = pc/100
            val_x = int(i*4+150)
            val_y = int(i*4+150)
            val_pres = int(i*55)
            print("Will send: x={}, y={}, press={} (pc={})".format(
                val_x,
                val_y,
                val_pres,
                pc))
            uinput.send_events([
                libevdev.InputEvent(libevdev.EV_ABS.ABS_X,
                                    value=val_x),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_Y,
                                    value=val_y),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE,
                                    value=val_pres),
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
            pc += direc
            if not already_pressed_one:
                print("Press!")
                uinput.send_events([
                    # Pen close to device
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                        value=1),
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                        value=1),
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                        value=0),
                ])                
                already_pressed_one = True
            if pc >= 100 or pc <=0 :
                print("Release click.")
                uinput.send_events([
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                        value=0),
                    # Pen outside of the position
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                        value=0),
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                        value=0),
                ])
                if pc >= 100:
                    pc = 100
                    direc = -1
                if pc <= 0:
                    pc = 0
                    direc = +1
                time.sleep(5)
                print("Press!")
                uinput.send_events([
                    # Pen close to device
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOOL_PEN,
                                        value=1),
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_TOUCH,
                                        value=1),
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT,
                                        value=0),
                ])
                already_pressed_one = True
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    except OSError as e:
        print(e)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: {}")
        sys.exit(1)
    main(sys.argv)