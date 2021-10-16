from flask import Flask, render_template, request
import json
import os
import csv
from pprint import pprint

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

app = Flask(__name__)

# DATA LOADING GOES HERE
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, 'data/irrigation_systems.json'), 'r', encoding='utf-8-sig') as f:
    irrigation_data = json.load(f)
with open(os.path.join(dirname, 'data/Irrigation_table - clean numeric ranges_fixed.csv'), 'r', encoding='utf-8-sig') as f:
    irrigation_table = list(csv.reader(f))
with open(os.path.join(dirname, 'data/Irrigation_table.csv'), 'r', encoding='utf-8-sig') as f:
    irrigation_table_raw = list(csv.reader(f))
with open(os.path.join(dirname, 'data/simulation/output.csv'), 'r') as f:
    regression_data = list(csv.reader(f))

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


@app.route('/irrigation')
def irrigation():
    return render_template('irrigation_model.html')


@app.route('/water_prediction')
def water_use():
    return render_template('regression_model.html')


@app.route('/methodology')
def methodology():
    return render_template('methodology.html')


# @app.route('/test_output', methods=['POST'])
# def test_output():
#     """Handles test form submissions from "models" page."""

#     # Get data from form
#     num_cows_text = request.form['test_input']
#     num_cows_range = request.form['test_range']

#     # A simple model
#     water_consumption_text = water_model(num_cows_text)
#     water_consumption_range = water_model(num_cows_range)

#     # Build response dictionary
#     response = {
#         "num_cows_text": num_cows_text,
#         "num_cows_range": num_cows_range,
#         "water_consumption_text": water_consumption_text,
#         "water_consumption_range": water_consumption_range,
#     }

#     # Serve modelled value to html template
#     return render_template('models.html', response=response)


@app.route('/regression_model', methods=['POST'])
def regression_model(test_data=None):

    # EXAMPLE REQUEST DATA
    # {'action': '',
    #  'farm_size': '123',
    #  'irrigation_percentage': '34',
    #  'lactating_cows': '324',
    #  'location': 'leongatha',
    #  'nonlactating_cows': '23',
    #  'water_usage': '32'}

    # Uncomment to see request data format
    # pprint(request.form)

    # Results dict
    results = {}

    # Convert immutable dict to mutable or handle test data
    if test_data:
        form_data = test_data
    else:
        form_data = dict(request.form)

    # Take column headers before filtering data
    column_headers = regression_data[0]

    # Coefficient dict and filter rows
    if str(form_data['irrigation_percentage']) in ['', '0']: # no irrigation
        intercept = -1.096 * 10**4
        coefficients = {
            "farm_size": (4.595, -2),
            "irrigation_percentage": (0, 0),
            "lactating_cows": (1.157, 2),
            "nonlactating_cows": (7.094, 1),
        }
        filtered_data = [x for x in regression_data if x[6] == 'no']
    else: # irrigation
        form_data["num_cows"] = int(form_data['lactating_cows']) + int(form_data['nonlactating_cows'])
        intercept = -2.308 * 10**7
        coefficients = {
            "farm_size": (5.343, 3),
            "irrigation_percentage": (3.775, 5),
            "lactating_cows": (-3.370, 2),
            "num_cows": (2.063, 2),
        }
        filtered_data = [x for x in regression_data if x[6] == 'yes']

    # Convert blank strings to 0
    for key in form_data.keys():
        if form_data[key] == '':
            form_data[key] = 0

    # Calculate regression model result
    result = intercept + sum([float(form_data[x]) * (coefficients[x][0] * 10**coefficients[x][1])
                  for x in coefficients.keys()])

    # Figure out water usage differential
    if form_data['water_usage'] != 0:
        actual = float(form_data['water_usage']) * 1000000 # megalitre
        diff = result - actual
        error = abs(((actual - result) / actual) * 100)
        usage = actual

        results['difference'] = diff
        results['error'] = error
        results['actual'] = actual
    else:
        usage = result

    # Create dataframe
    df = pd.DataFrame(filtered_data, columns=column_headers)
    df['avg_daily_water_usage'] = pd.to_numeric(df['avg_daily_water_usage'])
    
    # Sort by water consumption
    sorted_df = df.sort_values('avg_daily_water_usage').reset_index()
    sorted_df['rank'] = sorted_df.index / float(len(sorted_df) - 1)

    # Setup the interpolator using the value as the index
    interp = interp1d(sorted_df['avg_daily_water_usage'], sorted_df['rank'], fill_value="extrapolate")

    # Get quantile for measurement
    quantile = interp(usage)

    results['quantile'] = quantile
    results['output'] = result

    # Tidy up the results
    results['output'] = int(str(results['output']).split('.')[0]) # no decimal litres
    results['output'] = f"{results['output']:,}" # comma separators
    results['quantile'] = str(round(float(results['quantile']), 2)) # 2 d.p.
    if 'actual' in results.keys():
        results['actual'] = int(str(results['actual']).split('.')[0]) # no decimal litres
        results['actual'] = f"{results['actual']:,}" # comma separators
        results['difference'] = int(str(results['difference']).split('.')[0]) # no decimal litres
        results['difference'] = f"{results['difference']:,}" # comma separators
        results['error'] = str(round(float(results['error']), 2)) # 2 d.p.

    if test_data:
        return results
    else:
        return render_template('regression_model.html', response=results, form_data=form_data)



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

    # Catch empty fields
    keys = ["capital_cost", "pumping_cost",
            "labour_requirements", "efficiency", "uniformity"]
    for key in keys:
        if key not in request.form.keys():
            return render_template('irrigation_model.html', error="All form fields must have a value selected.")

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
    return render_template('irrigation_model.html', irri_response=recs)
