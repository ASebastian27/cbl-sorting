#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
import time
from picamera import PiCamera

def setup():       
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
    time.sleep(3)
    ser.reset_input_buffer()
    print("Ser ok")
    
    camera = PiCamera()
    camera.start_preview(alpha=255)
    time.sleep(10)
    camera.stop_preview()
    print("Camera ok")

try:
    setup()
    
    while True:
        if keyboard.is_pressed('p'):
            res = "red" #placeholder
            if res == "red":
                ser.write("red\n".encode('utf-8'))
            elif res == "blue":
                ser.write("blue\n".encode('utf-8'))
            elif res == 'green':
                ser.write("green\n".encode('utf-8'))
        elif keyboard.is_pressed('r'):
            ser.write("green\n".encode('utf-8'))
                
except KeyboardInterrupt:
    ser.write("green\n".encode('utf-8')) #restart servo in straight pos
    ser.close()
