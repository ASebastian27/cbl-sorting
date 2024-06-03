#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
from time import sleep

import sys
from hx711v0_5_1 import HX711
import numpy as np

from picamera import PiCamera
from picamera.array import PiRGBArray

import camLib
import weightLib

##GLOBAL VARIABLES
global camera
camera = PiCamera()

#Capacities
numberCapacities = np.array([0, 0, 0])
kgCapacities = np.array([0, 0, 0])

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.0)
def setup():
    ##Serial Communication Setup
    sleep(2)
    ser.reset_input_buffer()
    print("[INFO] Serial connection OK")
    
    '''
    Counting (with eth port DOWN)
    1 2
    3 4
    5 6
    7 8
    ...

    [HX1]
    VCC to Raspberry Pi + (3.3V : Pin 1, Pin 17)
    GND to Raspberry Pi Pin 6 (GND : Pin 6, Pin 9, Pin 14, Pin 20, 25, 30, 34, 39)
    DT to Raspberry Pi Pin 29 (GPIO 5 : Pin 29)
    SCK to Raspberry Pi Pin 31 (GPIO 6 : Pin 31)

    Other Combinations
    GPIO NRS    PIN NRS.
    (5,   6) -> (29, 31)
    (17, 22) -> (11, 13)
    (23, 24) -> (16, 18)
    (16, 26) -> (36, 37)
    '''
    ##HX711 Setup
    global hx1
    hx1 = HX711(5, 6)
    READ_MODE_POLLING_BASED = "--polling-based"
    READ_MODE = READ_MODE_POLLING_BASED
    hx1.setReadingFormat("MSB", "MSB")
    hx1.autosetOffset()
    offsetValue = hx1.getOffset()
    referenceUnit = 765
    hx1.setReferenceUnit(referenceUnit)
    if (offsetValue != 0):
        print("[INFO] HX1 connection OK")

    ##TODO: Modify based on text file from website...
    global numberCapacities
    numberCapacities = np.array([0,0,0])
    global kgCapacities
    kgCapacities = np.array([0,0,0])

def getSortingMode():
    # Get Sorting Mode from Website
    # ...
    return "COLOR_BASED"

def main():
    try:
        setup()
        camLib.cameraSetup(camera)

        while True:
            msg = "null"

            if keyboard.is_pressed('p'):
                sleep(1)
                msg = "load\n"
                ser.write(msg.encode('utf-8'))
                sleep(6)

                SORTING_MODE = getSortingMode()
                if SORTING_MODE == "COLOR_BASED":
                    color = camLib.readColor(camera)
                    camLib.handleErrors(color)
                    msg = str(camLib.colorToServoPos(color)) + "\n"
                    
                elif SORTING_MODE == "WEIGHT_BASED":
                    weightValue = weightLib.getGrams(hx1)
                    weightClass = weightLib.getWeightClass(weightValue)
                    msg = str(weightLib.weightClassToServoPos(weightClass)) + "\n"
                
                ser.write(msg.encode('utf-8'))
                print(msg)
                
    except Exception as e:
        print(e)
        camLib.closeAll(camera)
        return

if __name__ == "__main__":
    main()