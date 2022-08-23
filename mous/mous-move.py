##!usr/bin/python3

#Einbinden der Bibliotheken
import time
import dbus
import dbus.service
import dbus.mainloop.glib


class MouseClient():
	def __init__(self):
		super().__init__()
		self.state = [0, 0, 0, 0]
		self.bus = dbus.SystemBus()
		self.btkservice = self.bus.get_object(
			'org.thanhle.btkbservice', '/org/thanhle/btkbservice')
		self.iface = dbus.Interface(self.btkservice, 'org.thanhle.btkbservice')
	def send_current(self):
		try:
			self.iface.send_mouse(0, bytes(self.state))
		except OSError as err:
			error(err)

SCREEN_X = 1920
SCREEN_Y = 1200

X_OLD = SCREEN_X-1
Y_OLD = SCREEN_Y-1

#x_move and y_move must be between -127 and 127
def mouse_move (x_move, y_move, button):
	global X_OLD
	global Y_OLD
	global SCREEN_X
	global SCREEN_Y
	if(X_OLD + x_move >= SCREEN_X):
		X_OLD = SCREEN_X -1
	elif(X_OLD + x_move < 0):
		X_OLD = 0
	else:
		X_OLD = X_OLD + x_move
	
	if(Y_OLD + y_move >= SCREEN_Y):
		Y_OLD = SCREEN_Y -1
	elif(Y_OLD + y_move < 0):
		Y_OLD = 0
	else:
		Y_OLD = Y_OLD + y_move

	if(x_move < 0):
		x_move = 256 + x_move

	if(y_move < 0):
		y_move = 256 + y_move

	client = MouseClient()
	client.state[0] = button
	client.state[1] = x_move
	client.state[2] = y_move
	client.state[3] = 0
	client.send_current()

def mouse_abs(x, y, button):
	global X_OLD
	global Y_OLD
	global SCREEN_X
	global SCREEN_Y

	if(x < 0):
		x = 0
	elif(x >= SCREEN_X):
		x = SCREEN_X - 1

	if(y < 0):
		y = 0
	elif(y >= SCREEN_Y):
		y = SCREEN_Y - 1

	while(X_OLD != x) | (Y_OLD != y):
		x_diff = x - X_OLD
		y_diff = y - Y_OLD

		if(x_diff > 0):
			if(x_diff > 127):
				x_diff = 127
		elif(x_diff < 0):
			if(x_diff < -127):
				x_diff = -127

		if(y_diff > 0):
			if(y_diff > 127):
				y_diff = 127
		elif(y_diff < 0):
			if(y_diff < -127):
				y_diff = -127
	
		mouse_move(x_diff, y_diff, 0)

	mouse_move(0, 0, button)


#Reset auf 0,0
mouse_abs(0, 0, 0)


time.sleep(1)
mouse_abs(500, 500, 0)
time.sleep(1)
mouse_abs(700, 700, 0)
time.sleep(1)
mouse_abs(25, 25, 0)
time.sleep(1)
mouse_abs(-10, -100, 0)
time.sleep(1)
mouse_abs(504000, 58937474, 0)