#!/usr/bin/env python3
import serial
import time
import keyboard
import RPi.GPIO as GPIO
import time

s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10
wait = 0.0001


def setup():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(s2,GPIO.OUT)
  GPIO.setup(s3,GPIO.OUT)
  print("\n")

def readRed():
    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.LOW)
    time.sleep(wait)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start 
    red  = NUM_CYCLES / duration
    return red

def readBlue():
    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(wait)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    blue = NUM_CYCLES / duration
    return blue
    
def readGreen():
    GPIO.output(s2,GPIO.HIGH)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(wait)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    green = NUM_CYCLES / duration
    return green
    
def readColor():
    ser.write("green\n".encode('utf-8')) #restart servos in straight pos
    
    redCounter = 0
    blueCounter = 0
    greenCounter = 0
    
    redSum = 0.0
    greenSum = 0.0
    blueSum = 0.0
    
    for i in range (0, 1000):
        red = readRed()
        green = readGreen()
        blue = readBlue()
        
        redSum += red
        greenSum += green
        blueSum += blue
        
        # print(str(red) + " " + str(green) + " " + str(blue))
        
        debug = True
        if green < red and blue < red:
            redCounter += 1
            print("Reading " + str(i) + " " + 'red')
        elif red < green and blue < green:
            greenCounter += 1
            print("Reading " + str(i) + " " + 'green')
        elif green < blue  and red < blue:
            blueCounter += 1
            print("Reading " + str(i) + " " + 'blue')
            
    print("red: "+ str(redCounter) + " green: " + str(greenCounter) + " blue: " + str(blueCounter))
    print("redAvg: " + str(redSum/1000) + " green: " + str(greenSum/1000) + " blue: " + str(blueSum/1000))
    if redCounter >= greenCounter and redCounter >= blueCounter:
        return ("red")
    if blueCounter >= redCounter and blueCounter >= greenCounter:
        return ("blue")
    return("green")
        
        
ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1.0)
time.sleep(3)
ser.reset_input_buffer()
print("Ser ok")

try:
    setup()
    
    while True:
        if keyboard.is_pressed('p'):
            print('p')
            res = readColor()
            print(res)
            if res == "red":
                ser.write("red\n".encode('utf-8'))
            elif res == "blue":
                ser.write("blue\n".encode('utf-8'))
            elif res == 'green':
                ser.write("green\n".encode('utf-8'))
        elif keyboard.is_pressed('r'):
            ser.write("green\n".encode('utf-8'))
                
            
        '''
pppppprrrr
        red = readRed()
        blue = readBlue()
        green = readGreen()
        prpppppp
        if green < red and blue < red:
            print("red")
        if blue < green:
            print("green")
        if green < blue  and red < blue:
            print("blue")

        if keyboard.is_pressed('r'):
            print("Suuiiii")
            ser.write("Ronaldo\n".encode('utf-8'))
            time.sleep(3)
            ser.write("Maradona\n".encode('utf-8'))
        elif keyboard.is_pressed('m'):
            print("Ankara messi")
            ser.write("Messi\n".encode('utf-8'))
            time.sleep(3)
            ser.write("Maradona\n".encode('utf-8'))
        #time.sleep(1)
        #print("Suuiiii")
        #print("Ankara messi")
        #ser.write("Messi\n".encode('utf-8'))
        #ser.write("Maradona\n".encode('utf-8'))
        '''
except KeyboardInterrupt:
    ser.write("green\n".encode('utf-8')) #restart servo in straight pos
    ser.close()