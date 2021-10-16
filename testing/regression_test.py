import os
import csv

import sys
sys.path.insert(0,'..')

from app import regression_model

# Load data file
with open("regression_dataset.csv", 'r') as f:
    regression_data = list(csv.reader(f))

# Store errors
irrigating_error = []
nonirrigating_error = []

# Loop through each row in the test data
for row in regression_data[1:]:
    form_data = {
        "location": row[1],
        "lactating_cows": row[3],
        "nonlactating_cows": row[4],
        "farm_size": row[5],
        "irrigation_percentage": row[7],
        "water_usage": float(row[10]) / 1000000
    }

    results = regression_model(form_data)

    if float(results['output'].replace(',', '')) < 0:
        print(results)
        print(form_data['irrigation_percentage'])