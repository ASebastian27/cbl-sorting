#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
from time import sleep

from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

import sys
from hx711v0_5_1 import HX711

#Declare red bounds
redLower = np.array([160, 150, 50])
redUpper = np.array([180, 255, 255])

#declare blue bounds
blueLower = np.array([100, 150, 50])
blueUpper = np.array([125, 255, 255])

#declare green bounds
greenLower = np.array([50, 150, 25])
greenUpper = np.array([80, 255, 255])

##GLOBAL VARIABLES
readAttempts = 0
BOLD = "\033[1m"

redBaseVal = 0
blueBaseVal = 0
greenBaseVal = 0

#Capacities
numberCapacities = np.array([0, 0, 0])
kgCapacities = np.array([0, 0, 0])

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
def setup():
    ##Serial Communication Setup
    sleep(2)
    ser.reset_input_buffer()
    print("Serial connection OK")
    
    ##Camera Setup
    global camera
    global rawCapture
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size = (640, 480))
    sleep(0.1)
    print("Camera connection OK")
    
    ##HX711 Setup
    hx1 = HX711(5, 6)

    ##TODO: Modify based on text file from website...
    global numberCapacities
    numberCapacities = np.array([0,0,0])
    global kgCapacities
    kgCapacities = np.array([0,0,0])

def closeAll():
    camera.close()
    ser.write("free\n".encode('utf-8'))
    ser.close()

def readColor():
    TOTAL_READINGS = 10
    BIG_DIFF = 1000000
    REREAD_ATTEMPTS = 3
    
    global readAttempts
    
    exitCount = 0
    redCount = 0
    greenCount = 0
    blueCount = 0
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        rawCapture.truncate(0)
        if exitCount == TOTAL_READINGS:
            break
        else:
            exitCount += 1
            
        img = frame.array
    
        #convert each frame to HSV and apply masks
        hsvImage = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        redMask = cv2.inRange(hsvImage, redLower, redUpper)
        greenMask = cv2.inRange(hsvImage, greenLower, greenUpper)
        blueMask = cv2.inRange(hsvImage, blueLower, blueUpper)
        
        #get pixel sums and print
        hasRed = np.sum(redMask) - redBaseVal
        hasGreen = np.sum(greenMask) - greenBaseVal
        hasBlue = np.sum(blueMask) - blueBaseVal
        print(str(exitCount) + " r:" + str(hasRed) + " g:" + str(hasGreen) + " b:" + str(hasBlue))
        
        # check whether there is a big difference between the colors
        # 1.000.000 seems to be a good confidence value
        if hasRed > hasGreen and hasRed - hasGreen > BIG_DIFF and hasRed > hasBlue and hasRed - hasBlue  > BIG_DIFF:
            redCount += 1
            #print("red incr")
        elif hasGreen > hasRed and hasGreen - hasRed > BIG_DIFF and hasGreen > hasBlue and hasGreen - hasBlue > BIG_DIFF:
            greenCount += 1
            #print("green incr")
        elif hasBlue > hasRed and hasBlue - hasRed > BIG_DIFF and hasBlue > hasGreen and hasBlue - hasGreen > BIG_DIFF:
            blueCount += 1
            #print("blue incr")      
    print(str(redCount) + " " + str(greenCount) + " " + str(blueCount))
    
    #report color & reset attempt counter
    if redCount > blueCount and redCount > greenCount and redCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("red")
    elif blueCount > redCount and blueCount > greenCount and blueCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("blue")
    elif greenCount > redCount and greenCount > blueCount and greenCount >= int(TOTAL_READINGS/2):
        readAttempts = 0
        return("green")
    else:
        if readAttempts >= int(REREAD_ATTEMPTS-1): #retrying a number of times
            #print("BUZZ!!!")                      #before throwing an error
            return("error")
        print("Reading not accurate. Trying again.\n*")
        readAttempts += 1
        return(readColor())
        
def main():
    try:
        setup()
        while True:
            msg = "null"
            if keyboard.is_pressed('p'):
                color = readColor()
                if color == "error":
                    raise Exception(BOLD + "[!] Error reading object.")
                msg = str(color) + "\n"
                ser.write(msg.encode('utf-8'))
                print(msg)
    except Exception as e:
        print(e)
        closeAll()
        return

if __name__ == "__main__":
    main()