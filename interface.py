from flask import Flask, render_template, request, jsonify
import driveFunctions

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
            driveFunctions.sortByColor()
    return render_template('Baneasa.html')

@interface.route('/weight', methods=['GET', 'POST'])
def weight():
    if request.method == 'POST':
        if request.form.get('sorting') == "color":
            interface.logger.info('COLOR OK')
            driveFunctions.sortByWeight() 
    return render_template('Dristor.html')



if __name__ == '__main__':
    interface.run(debug=True, host='0.0.0.0', port=5000)