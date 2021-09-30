import matplotlib.pyplot as plt
import csv

from numpy.lib.financial import irr

with open('output.csv', 'r') as f:
    data = csv.reader(f)
    data = list(data)
    data = data[1:]

print(f"MAX LACTATING: {max([int(x[3]) for x in data])}")
print(f"MAX NONLACTATING: {max([int(x[4]) for x in data])}")
print(f"MAX FARMSIZE: {max([int(x[5]) for x in data])}")
print(f"MAX WATER USAGE: {max([float(x[10]) for x in data])}")

while True:

    # Irrigation filter
    irrigation_index = 6
    irrigation_filter = input("Irrigation filter mode (only/none/default)")
    if irrigation_filter == 'only':
        filt_data = [x for x in data if x[irrigation_index] == 'yes'] 
    elif irrigation_filter == 'none':
        filt_data = [x for x in data if x[irrigation_index] == 'no'] 
    elif irrigation_filter == 'exit':
        raise SystemExit

    x_axis = int(input("Which index on x axis?"))
    x_label = input("What is the x attribute?")
    y_axis = int(input("Which index on y axis?"))
    y_label = input("What is the y attribute?")
    plt.scatter(
        [float(x[x_axis]) for x in filt_data],
        [float(x[y_axis]) for x in filt_data],
        alpha=0.5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()