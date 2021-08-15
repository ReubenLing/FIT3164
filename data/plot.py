import matplotlib.pyplot as plt
import csv

with open('output.csv', 'r') as f:
    data = csv.reader(f)
    data = list(data)
    data = data[1:]

plt.scatter(
    [float(x[2]) for x in data],
    [float(x[4]) for x in data],
    # c=[x[1] for x in data],
    # s=[x[3] for x in data],
    alpha=0.5)
plt.xlabel('Cows')
plt.ylabel('Consumption')
plt.show()