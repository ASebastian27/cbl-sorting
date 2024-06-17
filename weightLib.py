#!/usr/bin/env python3

import sys
from hx711v0_5_1 import HX711
import numpy as np
import statistics
from time import sleep

from exceptions import *
from playsound import playsound

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
    gramsList = []
    for i in range (0, 30):
        rawBytes = hx.getRawBytes()
        weightValue = hx.rawBytesToWeight(rawBytes)
        gramsList.append(weightValue)
    
    #Prints entire array.
    #print(gramsList[:])
    med = statistics.median(gramsList)
    print(f"[INFO] Median registered: {med}")
    if (med > 20):
        raise UnknownWeightException
    return med

def weightClassToServoPos(weightClass):
    '''
    LIGHT -> first
    MEDIUM -> second
    HEAVY -> third
    '''
    servoPos = ""
    if weightClass == "heavy":
        servoPos = "second"
    elif weightClass == "light":
        servoPos = "first"
    elif weightClass == "UNKNOWN":
        servoPos = "third"
    return servoPos

def getWeightClass(weight):
    if weight > 2 and weight < 10:
        return "light"
    elif weight > 10 and weight < 20:
        return "heavy"
    return "UNKNOWN"

def hxReset(hx):
    sleep(0.5)
    hx.autosetOffset()

def verifyWeight(a, b, delta):
    if (abs(a-b) <= delta):
        return True
    return False