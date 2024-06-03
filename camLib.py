#!/usr/bin/env python3

from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
from time import sleep

global rawCapture
global piCamera
BOLD = "\033[1m"

##Camera Setup
def cameraSetup(camera):
    global rawCapture
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size = (640, 480))
    sleep(0.1)
    print("Camera connection OK")

##Colors Definitions
redLower = np.array([160, 150, 50])
redUpper = np.array([180, 255, 255])

blueLower = np.array([100, 150, 20])
blueUpper = np.array([120, 255, 255])

greenLower = np.array([35, 150, 25])
greenUpper = np.array([100, 255, 175])

readAttempts = 0
redBaseVal = 100000
blueBaseVal = 2000
greenBaseVal = 1000000

def closeAll(camera):
    camera.close()

def readColor(camera):
    TOTAL_READINGS = 10       # Number of sub-readings per reading
    BIG_DIFF = 1000000        # Min difference between values to conclude presence of a color
    REREAD_ATTEMPTS = 3       # Number of times to re-attempts reading TOTAL_READING times before throwing
    CUBE_THRESHOLD = 10000000 # Min value in a reading to conclude presence of a cube in frame
    
    global readAttempts
    
    exitCount = 0
    redCount = 0
    greenCount = 0
    blueCount = 0
    tooManyPixels = 0
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        rawCapture.truncate(0)
        if exitCount == TOTAL_READINGS:
            break
        else:
            exitCount += 1
            
        img = frame.array
    
        # convert each frame to HSV and apply masks
        hsvImage = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        redMask = cv2.inRange(hsvImage, redLower, redUpper)
        greenMask = cv2.inRange(hsvImage, greenLower, greenUpper)
        blueMask = cv2.inRange(hsvImage, blueLower, blueUpper)
        
        # get pixel sums and print
        hasRed = max((np.sum(redMask) - redBaseVal), 0)
        hasGreen = max((np.sum(greenMask) - greenBaseVal), 0)
        hasBlue = max((np.sum(blueMask) - blueBaseVal), 0)
        print(str(exitCount) + " r:" + str(hasRed) + " g:" + str(hasGreen) + " b:" + str(hasBlue))
        
        # check whether there is a big difference between the colors
        # 1.000.000 seems to be a good confidence value
        if (hasRed > hasGreen and hasRed - hasGreen > BIG_DIFF and 
            hasRed > hasBlue and hasRed - hasBlue  > BIG_DIFF and hasRed > CUBE_THRESHOLD):
            redCount += 1
            #print("red incr")
        elif (hasGreen > hasRed and hasGreen - hasRed > BIG_DIFF and 
              hasGreen > hasBlue and hasGreen - hasBlue > BIG_DIFF and hasGreen > CUBE_THRESHOLD):
            greenCount += 1
            #print("green incr")
        elif (hasBlue > hasRed and hasBlue - hasRed > BIG_DIFF and 
              hasBlue > hasGreen and hasBlue - hasGreen > BIG_DIFF and hasBlue > CUBE_THRESHOLD):
            blueCount += 1
            #print("blue incr")     

        if (hasRed > CUBE_THRESHOLD*2 or hasGreen > CUBE_THRESHOLD*2 or hasBlue > CUBE_THRESHOLD*2):
            tooManyPixels += 1
        elif (hasRed + hasGreen + hasBlue > int(CUBE_THRESHOLD*2.5)):
            tooManyPixels += 1
    print(str(redCount) + " " + str(greenCount) + " " + str(blueCount))
    
    #report color & reset attempt counter
    if tooManyPixels >= int(TOTAL_READINGS/2):
        return("OVERFLOW_ERROR")
    
    elif redCount > blueCount and redCount > greenCount and redCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("red")
    elif blueCount > redCount and blueCount > greenCount and blueCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("blue")
    elif greenCount > redCount and greenCount > blueCount and greenCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("green")
    else:
        if readAttempts >= int(REREAD_ATTEMPTS-1): # retrying a number of times
            #print("BUZZ!!!")                      # before throwing an error
            return("READING_ERROR")
        print("Reading not accurate. Trying again.\n*")
        readAttempts += 1
        return(readColor(camera))
    
def colorToServoPos(color):
    '''
    RED -> First
    BLUE -> Second
    GREEN -> Last
    '''
    servoPos = "third"

    if color == "red":
        servoPos = "first"
    elif color == "blue":
        servoPos = "second"
    return servoPos

def handleErrors(color):
    if (color == "READING_ERROR"):
        raise Exception(BOLD + "[!] Error reading object. Is the camera blocked?")
    elif (color == "OVERFLOW_ERROR"):
        raise Exception(BOLD + "[!] Too much color in frame. Is it too crowded?")