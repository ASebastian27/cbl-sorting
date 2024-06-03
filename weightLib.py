#!/usr/bin/env python3

import sys
from hx711v0_5_1 import HX711
import numpy as np
import statistics

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
    print(gramsList[:])
    med = statistics.median(gramsList)
    print(f"[INFO] Median returned: {med}")

    return med

def weightClassToServoPos(weightClass):
    '''
    LIGHT -> first
    MEDIUM -> second
    HEAVY -> third
    '''
    servoPos = ""
    if weightClass == "heavy":
        servoPos = "third"
    elif weightClass == "medium":
        servoPos = "second"
    elif weightClass == "light":
        servoPos = "first"
    return servoPos

def getWeightClass(weight):
    if weight > 5 and weight < 10:
        return "light"
    elif weight > 10 and weight < 25:
        return "medium"
    return "heavy"