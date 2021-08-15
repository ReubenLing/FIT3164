from flask import Flask, render_template, request

app = Flask(__name__)

@ app.route('/')
def homepage():
    return render_template('index.html')

@ app.route('/models')
def models():
    return render_template('models.html')

@ app.route('/methodology')
def methodology():
    return render_template('methodology.html')

@ app.route('/test_output', methods=['POST'])
def test_output():

    # Get data from form
    try:
        num_cows = int(request.form['test_input'])
    except ValueError: # ideally validate in frontend, this method for testing only
        return render_template('models.html', response="Bad input, must be integer")

    # A model
    water_consumption = num_cows * 44.5

    # Build response dict
    response = {
        "num_cows": num_cows,
        "water_consumption": water_consumption
    }

    # Serve modelled value to html template
    return render_template('models.html', response=response)
