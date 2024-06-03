#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
from time import sleep

import sys
from hx711v0_5_1 import HX711

import camLib

READ_MODE_INTERRUPT_BASED = "--interrupt-based"
READ_MODE_POLLING_BASED = "--polling-based"
READ_MODE = READ_MODE_POLLING_BASED

if READ_MODE == READ_MODE_POLLING_BASED:
    print("[INFO] Read mode is 'polling based'.")
else:
    print("[INFO] Read mode is 'interrupt based'.")
    
'''
VCC to Raspberry Pi 3.3V Pin
GND to Raspberry Pi Pin 6 (GND)
DT to Raspberry Pi Pin 29 (GPIO 5)
SCK to Raspberry Pi Pin 31 (GPIO 6)
'''

##GLOBAL VARIABLES
global camera
BOLD = "\033[1m"

#Capacities
numberCapacities = np.array([0, 0, 0])
kgCapacities = np.array([0, 0, 0])

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
def setup():
    ##Serial Communication Setup
    sleep(2)
    ser.reset_input_buffer()
    print("Serial connection OK")
    
    ##HX711 Setup
    global hx1
    hx1 = HX711(5, 6)
    hx1.setReadingFormat("MSB", "MSB")
    hx1.autosetOffset()
    offsetValue = hx1.getOffset()
    referenceUnit = 765
    hx1.setReferenceUnit(referenceUnit)

    ##TODO: Modify based on text file from website...
    global numberCapacities
    numberCapacities = np.array([0,0,0])
    global kgCapacities
    kgCapacities = np.array([0,0,0])

def printRawBytes(hx, rawBytes):
    print(f"[RAW BYTES] {rawBytes}")

def printLong(hx, rawBytes):
    print(f"[LONG] {hx.rawBytesToLong(rawBytes)}")

def printLongWithOffset(hx, rawBytes):
    print(f"[LONG WITH OFFSET] {hx.rawBytesToLongWithOffset(rawBytes)}")

def printWeight(hx, rawBytes):
    print(f"[WEIGHT] {hx.rawBytesToWeight(rawBytes)} gr")
    
def getWeight(hx, rawBytes):
    return hx.rawBytesToWeight(rawBytes)

def printAll(hx, rawBytes):
    longValue = hx.rawBytesToLong(rawBytes)
    longWithOffsetValue = hx.rawBytesToLongWithOffset(rawBytes)
    weightValue = hx.rawBytesToWeight(rawBytes)
    print(f"[INFO] INTERRUPT_BASED | longValue: {longValue} | longWithOffsetValue: {longWithOffsetValue} | weight (grams): {weightValue}")

def getRawBytesAndPrintAll(hx):
    rawBytes = hx.getRawBytes()
    longValue = hx.rawBytesToLong(rawBytes)
    longWithOffsetValue = hx.rawBytesToLongWithOffset(rawBytes)
    weightValue = hx.rawBytesToWeight(rawBytes)
    print(f"[INFO] POLLING_BASED | longValue: {longValue} | longWithOffsetValue: {longWithOffsetValue} | weight (grams): {weightValue}")

def getGrams(hx):
    rawBytes = hx.getRawBytes()
    weightValue = hx.rawBytesToWeight(rawBytes)
    return weightValue
    
def getWeightClass(weightValue):
    if(weightValue < 15 and weightValue > 5):
        weightClass = "red"
    elif(weightValue < 40 and weightValue >15):
        weightClass = "blue"
    elif(weightValue > 40):
        weightClass = "green"
    return weightClass

def weightClassToServoPos(weightClass):
    servoPos = 0
    if weightClass == "heavy":
        servoPos = 0
    elif weightClass == "medium":
        servoPos = 65
    elif weightClass == "light":
        servoPos = 135
    return servoPos

def colorToServoPos(color):
    servoPos = 0
    if color == "red":
        servoPos = 65
    elif color == "blue":
        servoPos = 135
    return servoPos

def getWeightClass(weight):
    if weight > 5 and weight < 10:
        return "light"
    elif weight > 10 and weight < 25:
        return "medium"
    return "heavy"

def main():
    try:
        setup()
        camLib.cameraSetup(camera)

        while True:
            msg = "null"
            if keyboard.is_pressed('p'):
                sleep(0.5)
                msg = "load\n"
                ser.write(msg.encode('utf-8'))
                sleep(6)
                
                color = camLib.readColor()
                if color == "error":
                    raise Exception(BOLD + "[!] Error reading object.")
                msg = str(colorToServoPos(color)) + "\n"
                ser.write(msg.encode('utf-8'))
                
                print(msg)
            elif keyboard.is_pressed('g'):
                sleep(0.5)
                msg = "load\n"
                ser.write(msg.encode('utf-8'))
                sleep(6)
                
                weightValue = getGrams(hx1)
                print(weightValue)
                weightClass = getWeightClass(weightValue)
                msg = str(weightClassToServoPos(weightClass)) + "\n"
                ser.write(msg.encode('utf-8'))
                #print(msg)
                
    except Exception as e:
        print(e)
        camLib.closeAll(camera)
        return

if __name__ == "__main__":
    main()