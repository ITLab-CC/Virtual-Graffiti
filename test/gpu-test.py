import cv2
import numpy as np

MASK_COLORS=[0, 179, 0, 255, 0, 145, 1]

cap = cv2.VideoCapture(0)

# Read the images as normal
# npMat1 = cv2.imread("path_to_image_to_be_corrected")
Running = True
while(Running):
    success, org_img = cap.read()

    # Load the images onto the GPU
    img = cv2.cuda_GpuMat()
    img.upload(org_img)

    # Convert the color on the GPU
    imgHSV = cv2.cuda.cvtColor(img,cv2.COLOR_BGR2HSV)
    lower = (MASK_COLORS[0],MASK_COLORS[2],MASK_COLORS[4], 0)
    upper = (MASK_COLORS[1],MASK_COLORS[3],MASK_COLORS[5], 0)
    mask = cv2.cuda.inRange(imgHSV, lower, upper)

    # Create the CUDA ORB detector and detect keypoints/descriptors
    # orb = cv2.cuda.ORB_create(nfeatures=100)
    # kp, descs = orb.detectAndComputeAsync(mask, None) # Both are returned as GPU Mats
    # kp = orb.convert(kp)

    hcd = cv2.cuda.createHoughCirclesDetector(1, 100, 120, 10, 20, 100, 1)
    kp = hcd.detect(mask)
    kp = kp.download()
    # print(kp)

    if kp is not None:
        print(kp[0][0])
        mask = mask.download()
        org_img = cv2.circle(org_img,(int(kp[0][0][0]),int(kp[0][0][1])), int(kp[0][0][2]), (0,0,255), 2, cv2.LINE_AA)

    # img = cv2.drawKeypoints(org_img, kp, None)

    cv2.imshow('Debug', org_img)
    if cv2.waitKey(1) & 0xFF == 113:
        cv2.destroyAllWindows()
        Running = False