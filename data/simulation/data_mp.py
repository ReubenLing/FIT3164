import numpy as np
import json
import csv
import matplotlib.pyplot as plt
from pprint import pprint
import multiprocessing as mp

# Irish data regression
"""
Coefficients:
Estimate Std. Error t value Pr(>|t|)
(Intercept)                        -1.164e+07  6.911e+06  -1.684  0.11436
ï..Farm..                           6.040e+04  4.339e+04   1.392  0.18569
Farm.area..Ha.a                    -5.177e+04  2.482e+04  -2.086  0.05577 .
Milk.sales..kg.FPCM.year.b         -4.203e+01  1.374e+01  -3.058  0.00851 **
X..Cows                             1.157e+05  5.027e+04   2.301  0.03728 *
Milk.production.Cow..kg.FPCM.year.  3.453e+03  1.226e+03   2.817  0.01370 *
Concentrate..T.DM.year.c            3.588e+04  1.586e+04   2.263  0.04006 *
Grass.grown..T.DM.year.             3.062e+04  1.372e+04   2.231  0.04253 *
Imported.forages..T.DM.             1.124e+04  4.643e+03   2.420  0.02970 *
Kg.feed.Cow.per.year               -1.542e+03  1.045e+03  -1.477  0.16194
"""

# ATTRIBUTES TO ADD
# - proportion of cow types
# - number of people living in house

# Edit values
variables = {
    # Basic parameters
    # "farms": 3462,  # https://www.dairyaustralia.com.au/industry-statistics/cow-and-farms-data
    "farms": 1000,  # https://www.dairyaustralia.com.au/industry-statistics/cow-and-farms-data
    "cows_per_farm": 895,
    "farm_size_avg": 4331,  # hectares

    # Farm usage parameters
    "lactating_proportion": 66.8, # percent
    "lactating_demand": 80,
    "nonlactating_demand": 50,
    "variation_max_mult": 19, # 19 = 1.8

    # Irrigation parameters
    "farms_irrigation_proportion": 55, # percent
    "irrigated_land_proportion": 64, # percent
    "water_per_irrigated_hectare": 8487, # litres per day

    # Yard cleaning
    "cleaning": 28 # litres per cow
}
# Start building table of data
attributes = [
    'farm_name',
    'location',
    'num_cows',
    'num_cows_lactating',
    'num_cows_other',
    'farm_size',
    'irrigating?',
    'irrigation_percentage',
    'rainfall',
    'evaporation',
    # 'tank_volume',
    'avg_daily_water_usage',
]

dataset = [attributes]

# Load location data
with open('attrs.json', 'r') as f:
    loc_data = json.load(f)
loc_data = loc_data['locations']

# Offset function
def offset(usage):
    max_offset = int(0.3 * usage) + 10000
    if np.random.randint(10) > 7:
        max_offset += int(np.random.normal(8000, 2000))
    offset = np.random.choice(range(-max_offset, max_offset))
    if usage + offset < 0:
        return abs(offset) 
    return offset

def generate_row(i):
        # Farm location - pick a random location, equal distribution
    farm_location = np.random.choice([x['location'] for x in loc_data])

    # Number of cows - normally distributed from average
    farm_cows = abs(int(np.random.normal(variables['cows_per_farm'], 300)))

    # Number of lactating cows -
    lactating_proportion = np.random.normal(variables['lactating_proportion'], 5)
    lactating_cows = int(farm_cows * (lactating_proportion / 100))

    # Number of non-lactating cows - simply the remaining
    non_lactating_cows = farm_cows - lactating_cows

    # Size of farm - normal distribute
    farm_size = abs(int(np.random.normal(variables['farm_size_avg'], 2000)))
    if farm_size < 1000:
        farm_size += 1000

    # Is the farm irrigating - take binary
    irrigating_proportion = variables['farms_irrigation_proportion'] / 100
    is_irrigating = np.random.choice(['yes', 'no'], p=[irrigating_proportion, 1-irrigating_proportion])

    # What percentage of farmland is being irrigated?
    if is_irrigating == 'yes':
        irrigated_percentage = np.random.normal(variables['irrigated_land_proportion'], 20)
        if irrigated_percentage > 90:
            irrigated_percentage -= 10
    else:
        irrigated_percentage = 0

    # Get location and evap data from location data
    rainfall = [x for x in loc_data if x['location']
                == farm_location][0]['rainfall']
    evaporation = [x for x in loc_data if x['location']
                   == farm_location][0]['evaporation']

    # Rainwater tank size - correlates to size of farm
    # farm_range = farm_size_max

    # Calculate usage
    usage = lactating_cows * variables['lactating_demand'] + non_lactating_cows * variables['nonlactating_demand']
    usage = usage * (np.random.choice(range(10, variables['variation_max_mult'])) / 10)
    usage += variables['water_per_irrigated_hectare'] * (farm_size * irrigated_percentage / 100)

    usage += offset(usage)

    # Add
    farm_data = [
        i,
        farm_location,
        farm_cows,
        lactating_cows,
        non_lactating_cows,
        farm_size,
        is_irrigating,
        irrigated_percentage,
        rainfall,
        evaporation,
        usage,
    ]
    print(farm_data)
    return farm_data

if __name__ == "__main__":
    p = mp.Pool()
    results = p.map(generate_row, range(variables['farms']))
    dataset += results
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(dataset)

    print('ROW HEADERS')
    pprint([f"{y} {x}" for y, x in enumerate(['index', 'farm location', 'number of cows', 'number of lactating cows', 'number of non-lactating cows', 'farm size', 'irrigating?', 'percentage of land irrigated', 'rainfall', 'evaporation', 'daily water usage'], 0)])