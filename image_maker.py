from matplotlib import pyplot as plt
import numpy as np

sampled = []
time = []
data = []

with open("logs/meter_1.txt", "r") as f:
    for l in f:
        if l[0] == 's':
            sampled += [int(l.split()[1])]
        else:
            d, t = l.split()[:2]
            time += [float(t)]
            data += [float(d)]


def find_nearest_time(array, value):
    array = np.array(array).T
    idx = (np.abs(array[:, 1] - value)).argmin()
    return array[idx][0]

plt.plot(time, data)

for t in sampled:
    nearest = find_nearest_time(np.array([data, time]), t)
    plt.plot(t, 0, marker="o", markersize=5, markeredgecolor="Black", markerfacecolor="red")

plt.show()

