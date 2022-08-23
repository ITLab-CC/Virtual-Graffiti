from turtle import width
import cv2
import numpy as np 

cap = cv2.VideoCapture(0)
cap.set(3,1920)
cap.set(4,1080)

def empty():
    pass


# cv2.namedWindow("TrackBars")
# cv2.resizeWindow("TrackBars",640,240)
# cv2.createTrackbar("Hue Min","TrackBars",0,179, empty)
# cv2.createTrackbar("Hue Max","TrackBars",179,179,empty)
# cv2.createTrackbar("Sat Min","TrackBars", 0,255, empty)
# cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
# cv2.createTrackbar("Val Min","TrackBars",0,255, empty)
# cv2.createTrackbar("Val Max","TrackBars",255,255,empty)

h_min=0
h_max=179
s_min=0
s_max=255
v_min=0
v_max=145

while True:
    success, img = cap.read()
    img = cv2.resize(img,(720, 576),interpolation=cv2.INTER_LINEAR)
   # width,height = 250,350
   # pts1 = np.float32([[111,219],[287,188],[154,482],[352,440]])
   # pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
   # matrix = cv2.getPerspectiveTransform(pts1,pts2)
   # imgOutput = cv2.warpPerspective(img,matrix,(width,height))

    #cv2.imshow("Output",imgOutput)



    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
    # h_max = cv2.getTrackbarPos("Hue Max","TrackBars")
    # s_min = cv2.getTrackbarPos("Sat Min","TrackBars")
    # s_max = cv2.getTrackbarPos("Sat Max","TrackBars")
    # v_min = cv2.getTrackbarPos("Val Min","TrackBars")
    # v_max = cv2.getTrackbarPos("Val Max","TrackBars")
    # print(h_min,h_max,s_min,s_max,v_min,v_max)


    lower = np.array([h_min,s_min,v_min])
    upper= np.array([h_max,s_max,v_max])
    mask = cv2. inRange (imgHSV, lower, upper)

    cv2. imshow("Original",img)
    # cv2. imshow("HSV",imgHSV)
    cv2. imshow("Mask", mask) 

    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break

