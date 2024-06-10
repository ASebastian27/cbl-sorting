#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
import cv2
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

BOLD = "\033[1m"

#Capacities
numberCapacities = np.array([0, 0, 0])
kgCapacities = np.array([0, 0, 0])

ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
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
    
    UNITS:
    HX1: 630
    HX2: 1000
    '''
    ##HX711 Setup
    global hx_list
    hx_list = []
    refunit_list = [775, 1000, 930, 915]
    global hx1
    hx1 = HX711(5, 6)
    hx_list.append(hx1)
    
    global hx2
    hx2 = HX711(17, 27)
    hx_list.append(hx2)
    
    global hx3
    hx3 = HX711(23, 24)
    hx_list.append(hx3)
    
    global hx4
    hx4 = HX711(19, 26)
    hx_list.append(hx4)
    
    READ_MODE_POLLING_BASED = "--polling-based"
    READ_MODE = READ_MODE_POLLING_BASED
    i = 0
    for hx in hx_list:
        hx.setReadingFormat("MSB", "MSB")
        hx.autosetOffset()
        offsetValue = hx.getOffset()
        referenceUnit = refunit_list[i]
        hx.setReferenceUnit(referenceUnit)
        i += 1
        print (offsetValue)
        if (offsetValue != 0):
            print(f"[INFO] HX{i} connection OK")

    ##TODO: Modify based on text file from website...
    global numberCapacities
    numberCapacities = np.array([0,0,0])
    global kgCapacities
    kgCapacities = np.array([0,0,0])
 
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

                SORTING_MODE = "COLOR_BASED"
                if SORTING_MODE == "COLOR_BASED":
                    color = camLib.readColor(camera)
                    print (f"Color is {color}! Item will be sorted to {color} bin.")
                    weightValue = weightLib.getGrams(hx1)
                    camLib.handleErrors(color)
                    msg = str(camLib.colorToServoPos(color)) + "\n"
                    
                elif SORTING_MODE == "WEIGHT_BASED":
                    weightValue = weightLib.getGrams(hx1)
                    weightClass = weightLib.getWeightClass(weightValue)
                    msg = str(weightLib.weightClassToServoPos(weightClass)) + "\n"
                
                ser.write(msg.encode('utf-8'))
                sleep(10)
                if color == "red":
                    print(str(weightLib.verifyWeight(weightValue, weightLib.getGrams(hx2), 4.5)))
                    print(weightLib.getGrams(hx2))
                elif color == "blue":
                    print(weightLib.verifyWeight(weightValue, weightLib.getGrams(hx3), 4.5))
                    print (weightLib.getGrams(hx3))
                elif color == "green":
                    print(weightLib.verifyWeight(weightValue, weightLib.getGrams(hx4), 4.5))
                    print (weightLib.getGrams(hx4))
                
                print(msg)
            if keyboard.is_pressed('r'):
                sleep(1)
                print(weightLib.getGrams(hx2))
                print("[INFO] Automatically setting the offset.")
                weightLib.hxReset(hx2)
                offsetValue = hx2.getOffset()
                print(f"[INFO] Finished automatically setting the offset. The new value is '{offsetValue}'.")
                print("[INFO] You can add weight now!")
                
    except Exception as e:
        print(e)
        camLib.closeAll(camera)
        return

if __name__ == "__main__":
    main()