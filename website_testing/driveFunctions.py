#!/usr/bin/env python3

import numpy as np
from time import sleep


#Capacities
numberCapacities = np.array([0, 0, 0])
webCapacities = np.array([2, 1, 3])

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
                #sortByColor()
                print("Sorting...")
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
                #sortByWeight()
                print("Sorting...")
                sleep(10) # Server side wait, prevents spamming.
                currentlySorting = 0
            except CapacityExceeded:
                return(render_template('capacitiesExceeded.html'))
            except LostObjectException:
                return(render_template('lostObject.html'))
    return render_template('weightButton.html')
##############################################################################
def main():
    try:
        print(1+1)
    except Exception as e:
        
        return

if __name__ == "__main__":
    main()
    interface.run(debug=True, host='0.0.0.0', port=5000)
