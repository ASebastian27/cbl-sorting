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
    
    UNITS:
    HX1: 630
    HX2: 1000
    '''
    ##HX711 Setup
    global hx_list
    hx_list = []
    refunit_list = [630, 1000, 0, 0]
    global hx1
    hx1 = HX711(5, 6)
    hx_list.append(hx1)
    
    global hx2
    hx2 = HX711(17, 27)
    hx_list.append(hx2)
    
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
                sleep(3)
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