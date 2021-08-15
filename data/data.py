import numpy as np
import json
import csv

# Edit values
# farms = 3462  # https://www.dairyaustralia.com.au/industry-statistics/cow-and-farms-data
farms = 500
cows_per_farm = 895
cow_usage = 44.5  # litres per day

# Start building table of data
attributes = [
    'farm_name',
    'location',
    'num_cows',
    'farm_size',
    'avg_monthly_water_usage',
]
dataset = [attributes]

# Load location data
with open('attrs.json', 'r') as f:
    loc_data = json.load(f)
loc_data = loc_data['locations']


# Offset function
def offset(usage):
    max_offset = int(0.3 * usage) + 10000
    if np.random.randint(10) > 8:
        max_offset += int(np.random.normal(8000, 2000))
    return np.random.choice(range(-max_offset, max_offset))


for i in range(farms):
    farm_location = np.random.choice([x['location'] for x in loc_data])
    farm_cows = abs(int(np.random.normal(895, 300)))
    farm_size = np.random.choice(range(100, 2000))
    usage = farm_cows * cow_usage
    farm_data = [i, farm_location, farm_cows, farm_size, usage + offset(usage)]
    dataset.append(farm_data)

with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(dataset)