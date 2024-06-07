from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import numpy as np
import cv2
import camLib
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size = (640, 480))
sleep(0.1)

redLower = np.array([160, 150, 50])
redUpper = np.array([180, 255, 255])

blueLower = np.array([93, 150, 25])
blueUpper = np.array([120, 255, 255])

green_bgr = np.uint8([[[100,200,100]]])
green_hsv = cv2.cvtColor(green_bgr,cv2.COLOR_BGR2HSV)
#print(green_hsv)

greenLower = np.array([36, 100, 25])
greenUpper = np.array([93, 255, 255]) #175

readAttempts = 0

redBaseVal = 0
blueBaseVal = 0
greenBaseVal = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
    img = frame.array
    #cv2.imshow("Frame", image)
    hsvImage = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    redMask = cv2.inRange(hsvImage, redLower, redUpper)
    greenMask = cv2.inRange(hsvImage, greenLower, greenUpper)
    blueMask = cv2.inRange(hsvImage, blueLower, blueUpper)
    
    hasRed = max((np.sum(redMask) - redBaseVal), 0)
    hasGreen = max((np.sum(greenMask) - greenBaseVal), 0)
    hasBlue = max((np.sum(blueMask) - blueBaseVal), 0)
    print("r:" + str(hasRed) + " g:" + str(hasGreen) + " b:" + str(hasBlue))
    
    cv2.imshow("red", redMask)
    cv2.imshow("green", greenMask)
    cv2.imshow("blue", blueMask)
    cv2.imshow("img", img)
    
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break