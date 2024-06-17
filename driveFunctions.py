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

##Capacities
numberCapacities = np.array([0, 0, 0])
webCapacities = np.array([0, 0, 0])

###################################################################
from flask import Flask, render_template, request, jsonify

interface = Flask(__name__)

#  interface.logger.info('COLOR')
@interface.route('/', methods=['GET', 'POST'])
def index():
    return render_template('landing.html')

@interface.route('/sorting', methods=['GET', 'POST'])
def sorting():
    if request.method == 'POST':
         data = request.get_json()
         webCapacities[0] = data.get("value1")
         webCapacities[1] = data.get("value2")
         webCapacities[2] = data.get("value3")
         print("[INFO] Web capacities")
         print(webCapacities[:])
         if request.form.get('start') == "confirm":
            interface.logger.info('ROBOT OK')
            return render_template('picker.html')
    return render_template('picker.html')
        
global currentlySorting
currentlySorting = 0

@interface.route('/color', methods=['GET', 'POST'])
def color():
    if request.method == 'POST':
        global currentlySorting
        if request.form.get('sorting') == "next" and currentlySorting == 0:
            interface.logger.info('SORT OK')
            try:
                currentlySorting = 1
                sortByColor()
                #print("Sorting...")
                sleep(10) # Server side wait, prevents spamming.
                currentlySorting = 0
            except CapacityExceeded:
                return(render_template('capacitiesExceeded.html'))
            except OverloadedCamException:
                return(render_template('overloadedCamera.html'))
            except BlockedCamException:
                return(render_template('blockedCamera.html'))
            except LostObjectException:
                return(render_template('lostObject.html'))
    return render_template('colorButton.html')

@interface.route('/weight', methods=['GET', 'POST'])
def weight():
    if request.method == 'POST':
        global currentlySorting
        if request.form.get('sorting') == "next" and currentlySorting == 0:
            interface.logger.info('SORT OK')
            try:
                currentlySorting = 1
                sortByWeight()
                #print("Sorting...")
                sleep(10) # Server side wait, prevents spamming.
                currentlySorting = 0
            except CapacityExceeded:
                return(render_template('capacitiesExceeded.html'))
            except LostObjectException:
                return(render_template('lostObject.html'))
    return render_template('weightButton.html')
##############################################################################

##GLOBAL VARIABLES
global camera
camera = PiCamera()

global ser
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
    global hx_list
    hx_list = []
    refunit_list = [900, 1000, 940, 445]
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

##Exceptions
class CapacityExceeded(Exception):
    "Raised when bin capacity was exceeded."
    pass
class BlockedCamException(Exception):
    "Raised when camera is possibly blocked."
    pass
class OverloadedCamException(Exception):
    "Raised when camera is possibly overloaded."
    pass
class UnknownWeightException(Exception):
    "Raised when a loadcell encountered an unknown weight."
    pass
class LostObjectException(Exception):
    "Raised when a loadcell encountered an unknown weight."
    pass
    
def sendLoadMessage():
    sleep(1)
    msg = "load\n"
    ser.write(msg.encode('utf-8'))
    sleep(6)

def sortByColor():
    # Reset all scales before sort
    for hx in hx_list:
        weightLib.hxReset(hx)
        sleep(1)
        print(str(hx) + " was reset. Current error is: " + str(weightLib.getGrams(hx)))

    camLib.cameraSetup(camera)  
    msg = "null"

    # Load item and analyze color & weight
    sendLoadMessage()
    color = camLib.readColor(camera)
    weightValue = weightLib.getGrams(hx1)

    # Can throw the following exceptions:
    # BlockedCamException, OverloadedCamException
    camLib.handleErrors(color)
    msg = str(camLib.colorToServoPos(color)) + "\n"
    if color == "red":
        if numberCapacities[0] < webCapacities[0]:
            sendMessage(msg)
            sleep(8)
            #verifyWeight() can throw LostObjectException
            if weightLib.verifyWeight(weightValue, weightLib.getGrams(hx2), 4.5) == True:
                numberCapacities[0] += 1
                print(numberCapacities[:])
                sleep(3)
        else:
            raise CapacityExceeded
    elif color == "blue":
        if numberCapacities[1] < webCapacities[1]:
            sendMessage(msg)
            #verifyWeight() can throw LostObjectException
            if weightLib.verifyWeight(weightValue, weightLib.getGrams(hx3), 4.5) == True:
                numberCapacities[1] += 1
                print(numberCapacities[:])
                sleep(3)
        else:
            raise CapacityExceeded
    elif color == "green":
        if numberCapacities[2] < webCapacities[2]:
            sendMessage(msg)
            #verifyWeight() can throw LostObjectException
            if weightLib.verifyWeight(weightValue, weightLib.getGrams(hx4), 4.5) == True:
                numberCapacities[2] += 1
                print(numberCapacities[:])
                sleep(3)
        else:
            raise CapacityExceeded
    return

def sortByWeight():
    # Reset all scales before weightsort
    for hx in hx_list:
        weightLib.hxReset(hx)
        sleep(1)
        print(str(hx) + " was reset. Current error is: " + str(weightLib.getGrams(hx)))

    msg = "null"
    sendLoadMessage()
    # Load item and analyze weight
    weightValue = weightLib.getGrams(hx1)
    weightClass = weightLib.getWeightClass(weightValue)

    msg = str(weightLib.weightClassToServoPos(weightClass)) + "\n"
    if weightClass == "light":
        if numberCapacities[0] < webCapacities[0]:
            sendMessage(msg)
            #verifyWeight() can throw LostObjectException
            if weightLib.verifyWeight(weightValue, weightLib.getGrams(hx2), 4.5) == True:
                numberCapacities[0] += 1
                print(numberCapacities[:])
                sleep(3)
        else:
            raise CapacityExceeded
    elif weightClass == "heavy":
        if numberCapacities[1] < webCapacities[1]:
            sendMessage(msg)
            #verifyWeight() can throw LostObjectException
            if weightLib.verifyWeight(weightValue, weightLib.getGrams(hx3), 4.5) == True:
                numberCapacities[1] += 1
                print(numberCapacities[:])
                sleep(3)
        else:
            raise CapacityExceeded
    elif weightClass == "UNKNOWN":
        raise UnknownWeightException
    return
    
def sendMessage(msg):
    ser.write(msg.encode('utf-8'))
    sleep(12)
    print(msg)
    return

def main():
    try:
        setup()
        camLib.cameraSetup(camera)              
    except Exception as e:
        print(e)
        camLib.closeAll(camera)
        return

if __name__ == "__main__":
    main()
    interface.run(debug=False, host='0.0.0.0', port=5000)
