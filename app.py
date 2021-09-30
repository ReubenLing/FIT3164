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
def regression_model():

    # EXAMPLE REQUEST DATA
    # {'action': '',
    #  'farm_size': '123',
    #  'irrigation_percentage': '34',
    #  'lactating_cows': '324',
    #  'location': 'leongatha',
    #  'nonlactating_cows': '23',
    #  'water_usage': '32'}

    # Uncomment to see request data format
    pprint(request.form)

    # Coefficient dict
    if request.form['irrigation_percentage'] == 0:
        coefficients = {
            "farm_size": 0,
            "irrigation_percentage": 0,
            "lactating_cows": 0,
            "nonlactating_cows": 0,
        }
    else:
        coefficients = {
            "farm_size": 0,
            "irrigation_percentage": 0,
            "lactating_cows": 0,
            "nonlactating_cows": 0,
        }

    result = sum([float(request.form[x]) * coefficients[x]
                  for x in coefficients.keys()])

    # Figure out water usage differential
    if request.form['water_usage'] != '':
        usage_diff = result - float(request.form['water_usage'])
        usage = request.form['water_usage']
    else:
        usage = result

    # Grade water consumption TODO 
    #   load csv
    #   sort by water usage
    #   use this shit

            #     import pandas as pd
            # import numpy as np
            # from scipy.interpolate import interp1d

            # # set up a sample dataframe
            # df = pd.DataFrame(np.random.uniform(0,1,(11)), columns=['a'])
            # # sort it by the desired series and caculate the percentile
            # sdf = df.sort('a').reset_index()
            # sdf['b'] = sdf.index / float(len(sdf) - 1)
            # # setup the interpolator using the value as the index
            # interp = interp1d(sdf['a'], sdf['b'])

            # # a is the value, b is the percentile
            # >>> sdf
            #     index         a    b
            # 0      10  0.030469  0.0
            # 1       3  0.144445  0.1
            # 2       4  0.304763  0.2
            # 3       1  0.359589  0.3
            # 4       7  0.385524  0.4
            # 5       5  0.538959  0.5
            # 6       8  0.642845  0.6
            # 7       6  0.667710  0.7
            # 8       9  0.733504  0.8
            # 9       2  0.905646  0.9
            # 10      0  0.961936  1.0

    return str(result)


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
            return render_template('models.html', error="All form fields must have a value selected.")

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
