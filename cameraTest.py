from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import numpy as np
import cv2
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size = (640, 480))
sleep(0.1)

redLower = np.array([160, 150, 50])
redUpper = np.array([180, 255, 255])

blueLower = np.array([100, 150, 50])
blueUpper = np.array([125, 255, 255])

greenLower = np.array([50, 150, 25])
greenUpper = np.array([80, 255, 255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array
    #cv2.imshow("Frame", image)
    hsvImage = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    redMask = cv2.inRange(hsvImage, redLower, redUpper)
    greenMask = cv2.inRange(hsvImage, greenLower, greenUpper)
    blueMask = cv2.inRange(hsvImage, blueLower, blueUpper)
    
    hasRed = np.sum(redMask)
    hasGreen = np.sum(greenMask)
    hasBlue = np.sum(blueMask)
    print("r:" + str(hasRed) + " g:" + str(hasGreen) + " b:" + str(hasBlue))
    
    cv2.imshow("red", redMask)
    cv2.imshow("green", greenMask)
    cv2.imshow("blue", blueMask)
    cv2.imshow("img", img)
    
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break