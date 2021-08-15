from flask import Flask, render_template, request

app = Flask(__name__)


# FUNCTIONS GO HERE
def water_model(cows):
    """Predict water usage."""

    # Model
    water_consumption = cows * 44.5

    # Formatting
    if water_consumption % 1 == 0:
        water_consumption = int(water_consumption)
    
    return water_consumption

# ROUTES GO HERE
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
        num_cows_text = int(request.form['test_input'])
        num_cows_range = int(request.form['test_range'])
    except ValueError: # ideally validate in frontend, this method for testing only
        return "Bad input, must be integer"

    # A simple model
    water_consumption_text = water_model(num_cows_text)
    water_consumption_range = water_model(num_cows_range)

    # Build response dictionary
    response = {
        "num_cows_text": num_cows_text,
        "num_cows_range": num_cows_range,
        "water_consumption_text": water_consumption_text,
        "water_consumption_range": water_consumption_range,
    }

    # Serve modelled value to html template
    return render_template('models.html', response=response)
