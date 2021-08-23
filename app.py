from flask import Flask, render_template, request
import json
import os
import csv
from pprint import pprint

app = Flask(__name__)

# DATA LOADING GOES HERE
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, 'data/irrigation_systems.json'), 'r', encoding='utf-8-sig') as f:
    irrigation_data = json.load(f)
with open(os.path.join(dirname, 'data/Irrigation_table - clean numeric ranges_fixed.csv'), 'r', encoding='utf-8-sig') as f:
    irrigation_table = list(csv.reader(f))
with open(os.path.join(dirname, 'data/Irrigation_table.csv'), 'r', encoding='utf-8-sig') as f:
    irrigation_table_raw = list(csv.reader(f))

# FUNCTIONS GO HERE
def water_model(cows):
    """Predict water usage."""

    # Validation - ideally validate in frontend, this method for testing only
    try:
        cows = int(cows)
    except ValueError:
        return "Bad input, must be integer"

    # Model
    water_consumption = cows * 44.5

    # Formatting
    if water_consumption % 1 == 0:
        water_consumption = int(water_consumption)

    return water_consumption


def irrigation_recommendation(input_dict):
    """Recommend an irrigation system"""

    # Range attributes
    fields = ['capital_cost', 'pumping_cost',
              'labour_requirements', 'efficiency', 'uniformity']

    # Format user input values to list
    user_values = [input_dict[x] for x in fields]

    # Loop through irrigation systems and rank
    recommendations = []
    for system in irrigation_table[1:]:
        current_sys_recs = []

        # Loop through attributes and match inputs
        for index in range(1, 6):
            if '-' in system[index]:  # range
                if int(user_values[index - 1]) in range(int(system[index][0]), int(system[index][3]) + 1):
                    current_sys_recs.append('green')
                else:
                    current_sys_recs.append('red')
            elif len(system[index]) == 1:  # single value
                if user_values[index - 1] == system[index]:
                    current_sys_recs.append('green')
                else:
                    current_sys_recs.append('red')
            else:  # shouldn't happen
                raise Exception

        # Append data to recs
        recommendations.append({
            'name': system[0],
            'matches': current_sys_recs,
            'score': len([x for x in current_sys_recs if x == "green"])})

    # Slice unwanted recommendations
    recommendations = recommendations[:int(input_dict['num_recs'])]

    return recommendations

# ROUTES GO HERE
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/models')
def models():
    return render_template('models.html')


@app.route('/methodology')
def methodology():
    return render_template('methodology.html')


@app.route('/test_output', methods=['POST'])
def test_output():
    """Handles test form submissions from "models" page."""

    # Get data from form
    num_cows_text = request.form['test_input']
    num_cows_range = request.form['test_range']

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


@app.route('/irrigation_proto', methods=['POST'])
def irrigation_proto():
    """Prototype irrigation model handler

    Response dictionary is a list of dicts. Each dict format:

    {
        "name": key name used in .csv files
        "fields": list of descriptive form of attributes from uncleaned table
        "matches": list that records how the input matched the attribute - 
                   green for a match, red for a non-match, 
                   corresponds to fields list
        "score": total number of matches
        "data": dictionary from irrigation_systems.json
    }

    Naive Bayes could replace "score"
    """

    # Uncomment to see request data format
    # pprint(request.form)

    # Get recommendations based on form data
    recs = irrigation_recommendation(request.form)

    # Join with other data for output
    for rec in recs:
        rec['data'] = irrigation_data[rec['name']]
        rec['fields'] = [x for x in irrigation_table_raw if x[0]
                         == rec['name']][0][1:6]

    # Sort recommendations by score
    recs.sort(key=lambda x: -int(x['score']))

    # Uncomment to see recommendation data format
    # pprint(recs[0])

    # Render template
    return render_template('models.html', irri_response=recs)
