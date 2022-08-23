##!usr/bin/python3

#Einbinden der Bibliotheken
import cv2
import numpy as np
import subprocess
import os

x_medium= 0
y_medium=0

# Maustaste zurücksetzen
subprocess.Popen(["./mouse_emulate.py"," 0 "," 0 "," 0 "," 0"])

cap = cv2.VideoCapture(1)

#Schleife für dauerhafte Bildübertragung
while 1:
	_, frame ,_ = cap.read()
	hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#Absteckung der Farberkennung
	lower= np.array([170,0,255])
	higher= np.array([255,255,255])

#Erkennung des größten Blobs
	mask = cv2.inRange(hsv_frame, lower, higher)
	_,contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)

#Speicherung der letzten Koordinaten
	x_last=x_medium
	y_last=y_medium

#Bestimmung der Mitte
	for cnt in contours:
		(x, y, w, h) = cv2.boundingRect(cnt)
		x_medium = int(((x+x+w)/2))
		y_medium = int(((y+y+h)/2))
		break
#Testbild anzeigen
	cv2.imshow("Frame", frame)
#Berechnung der Übergabevariablen
	x_dif=x_last-x_medium
	y_dif=y_last-y_medium

	if x_dif >= 0:
		x_rel = int((x_dif*(10))/50)
	elif x_dif < 0:
	   	x_rel = int((256-(x_dif*(-10))/50))
	if y_dif < 0:
	   	y_rel = int((y_dif*(-10))/38)
	elif y_dif >= 0:
	   	y_rel = int((256-(y_dif*10)/38))
	if y_rel == 256:
	   	y_rel = 0
	if x_rel == 256:
	   	x_rel = 0
#Umwandlung von int in string
	x = str(x_rel)
	y= str(y_rel)
#Variablenübergabe an Subprozess
	if x_rel==0 and y_rel==0:
		subprocess.Popen(["./mouse_emulate.py"," 0 ",x,y," 0 "])
	else:
		subprocess.Popen(["./mouse_emulate.py"," 1 ",x,y," 0 "])

	if cv2.waitKey(1) == ord("q"):
		break

#Beenden
cap.release()
cv2.destroyAllWindows()

