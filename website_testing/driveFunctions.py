#!/usr/bin/env python3

import numpy as np
from time import sleep


#Capacities
numberCapacities = np.array([0, 0, 0])
webCapacities = np.array([2, 1, 3])

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
         data = request.get_json()
         webCapacities[0] = data.get("value1")
         webCapacities[1] = data.get("value2")
         webCapacities[2] = data.get("value3")
         print("[INFO] Web capacities")
         print(webCapacities[:])
         if request.form.get('start') == "confirm":
            interface.logger.info('ROBOT OK')
            return render_template('americaNord.html')
    return render_template('americaNord.html')
        
@interface.route('/color', methods=['GET', 'POST'])
def color():
    if request.method == 'POST':
        if request.form.get('sorting') == "next":
            try:
                sortByColor()
                interface.logger.info('ColorSort OK')
            except Exception as e:
                return render_template('europa.html')
    return render_template('Baneasa.html')

@interface.route('/weight', methods=['GET', 'POST'])
def weight():
    if request.method == 'POST':
        if request.form.get('sorting') == "next":
            try:
                sortByColor()
                interface.logger.info('WeightSort OK')
            except Exception as e:
                return render_template('europa.html')
    return render_template('Dristor.html')
##############################################################
def main():
    try:
        print(1+1)
    except Exception as e:
        
        return

if __name__ == "__main__":
    main()
    interface.run(debug=True, host='0.0.0.0', port=5000)
