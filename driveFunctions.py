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
###########################################################
from flask import Flask, render_template, request, jsonify

interface = Flask(__name__)

#  interface.logger.info('COLOR')
@interface.route('/', methods=['GET', 'POST'])
def index():
    return render_template('americaCentrala.html')

@interface.route('/sorting', methods=['GET', 'POST'])
def sorting():
    if request.method == 'POST':
#         data = request.json
#         value1 = data.get('value1')
#         value2 = data.get('value2')
#         print(f"Received values: value1 = {value1}, value2 = {value2}")
        if request.form.get('start') == "confirm":
            interface.logger.info('ROBOT OK')
            return render_template('americaNord.html')
        
@interface.route('/color', methods=['GET', 'POST'])
def color():
    if request.method == 'POST':
        if request.form.get('sorting') == "next":
            interface.logger.info('SORT OK')
            sortByColor()
    return render_template('Baneasa.html')

@interface.route('/weight', methods=['GET', 'POST'])
def weight():
    if request.method == 'POST':
        if request.form.get('sorting') == "next":
            interface.logger.info('SORT OK')
            sortByWeight() 
    return render_template('Dristor.html')
##############################################################
##GLOBAL VARIABLES
global camera
camera = PiCamera()

#Capacities
numberCapacities = np.array([0, 0, 0])
kgCapacities = np.array([0, 0, 0])

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
    global hx1
    hx1 = HX711(5, 6)
    READ_MODE_POLLING_BASED = "--polling-based"
    READ_MODE = READ_MODE_POLLING_BASED
    hx1.setReadingFormat("MSB", "MSB")
    hx1.autosetOffset()
    offsetValue = hx1.getOffset()
    referenceUnit = 630
    hx1.setReferenceUnit(referenceUnit)
    if (offsetValue != 0):
        print("[INFO] HX1 connection OK")

    ##TODO: Modify based on text file from website...
    global numberCapacities
    numberCapacities = np.array([0,0,0])
    global kgCapacities
    kgCapacities = np.array([0,0,0])
    
def sendLoadMessage():
    sleep(1)
    msg = "load\n"
    ser.write(msg.encode('utf-8'))
    sleep(6)

def sortByColor():
    camLib.cameraSetup(camera)  
    msg = "null"
    sendLoadMessage()
    color = camLib.readColor(camera)
    camLib.handleErrors(color)
    msg = str(camLib.colorToServoPos(color)) + "\n"
    sendMessage(msg)
    return

def sortByWeight():
    msg = "null"
    sendLoadMessage()
    weightValue = weightLib.getGrams(hx1)
    weightClass = weightLib.getWeightClass(weightValue)
    msg = str(weightLib.weightClassToServoPos(weightClass)) + "\n"
    sendMessage(msg)
    return
    
def sendMessage(msg):
    ser.write(msg.encode('utf-8'))
    sleep(3)
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
