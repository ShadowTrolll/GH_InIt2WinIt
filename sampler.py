import asyncio
import aiofiles
import numpy as np
import time
import data_prompts

SLOPE = 0.2
TRESHOLD = 1
MINS_IN_DAY = 1440

SECONDS_IN_MINUTE = 60

FOLDER = "./logs/"

class Sampler():
    def __init__(self, id:int, expected_data:np.ndarray or None, save:bool) -> None:
        self.id = id
        if expected_data is None:
            self.fourier_data = None
        else:
            self.fourier_data = np.concatenate((expected_data, expected_data + np.array([0, expected_data[-1, 0]])), axis=0)
        self.day = 2
        self.datasets = None
        self.save = save

        self.sampled = []


    def time2minute(self):
        t = time.gmtime(time.time())
        m = t.tm_hour * 60 + t.tm_min
        return m 
    

    def compute_fourier(self):
        out = data_prompts.meter_fft(self.datasets[:-1])
        #print(self.id, "computing fourier", np.array(out).T)
        self.fourier_data = np.array(out).T
        return np.array(out).T
    

    def compute_wait_time(self, t, rewaiting:bool = False):
        if self.fourier_data is None:
            if self.datasets is None:
                return 100 if rewaiting else 5
            self.fourier_data = self.compute_fourier()

        #print("Here", self.fourier_data[:, 0] > (t + 3))
        future_data = self.fourier_data[(self.fourier_data[:, 0] > (t + 3))]
        multiples = np.array([1 + i * SLOPE for i in range(len(future_data))])

        #print(self.id, "future_data", future_data)

        future_data[:, 1] *= multiples

        goods = future_data[future_data[:, 1] > TRESHOLD]
        if len(goods) > 0:
            first_good_time = goods[0][0]
        else:
            first_good_time = t + 700

        return first_good_time - t


    def get_data(self):
        #return [np.array([[i * 5, np.random.rand()] for i in range(50)])]
        return data_prompts.create_dataset(self.id, False)


    async def write_to_files(self, new_data):
        print(self.id, "reading from file")
        try:
            async with aiofiles.open(FOLDER + 'meter_' + str(self.id) + ".txt", mode='r') as f:
                contents = await f.read()
                for i in range(len(contents), -1, -1):
                    if contents[i][0] == 's':
                        continue
                    latest_log = int(contents[i].split()[1])
                    break
            write_new = False
        except:
            write_new = True

        if write_new or len(new_data[new_data[:, 1] > latest_log]) == 0:
            async with aiofiles.open(FOLDER + 'meter_' + str(self.id) + ".txt", mode='w') as f:
                print(self.id, "writing to file", new_data.shape)
                for d in range(len(new_data) - 1):
                    to_write = str(new_data[d][0]) + " " + str(new_data[d][1]) + "\n"
                    await f.write(to_write)

                for s in self.sampled:
                    to_write = "s " + str(s) + "\n"
                    await f.write(to_write)

        else:
            new_data = new_data[new_data[:, 1] > latest_log]
            async with aiofiles.open(FOLDER + 'meter_' + str(self.id) + ".txt", mode='a') as f:
                print(self.id, "appending to file", new_data.shape)
                for d in range(len(new_data) - 1):
                    to_write = str(new_data[d][0]) + " " + str(new_data[d][1]) + "\n"
                    await f.write(to_write)

                for s in self.sampled:
                    to_write = "s " + str(s) + "\n"
                    await f.write(to_write)
        
        print("Finished writing", self.id)


    async def controler(self):
        while True:
            print("Computing wait time", self.id)
            wait_time = max(self.compute_wait_time(self.time2minute()), 5)
            print("Meter", self.id, "waiting", wait_time)

            await asyncio.sleep(wait_time * SECONDS_IN_MINUTE)

            datasets = self.get_data()
            self.sampled += [self.time2minute()]

            while datasets is None:
                wait_time = max(self.compute_wait_time(self.time2minute(), True) / 5, 5)
                print("Meter", self.id, "rewaiting", wait_time)
                await asyncio.sleep(wait_time * SECONDS_IN_MINUTE)
                datasets = self.get_data()
                self.sampled += [self.time2minute()]

            print("Meter", self.id, "GOT DATA", [d.shape for d in datasets])

            self.datasets = datasets

            if self.save:
                await self.write_to_files(datasets[-1])


from matplotlib import pyplot as plt

def find_nearest_time(array, value):
    array = np.array(array)
    #print("Min", array[:, 0])
    idx = (np.abs(array[:, 1] - value)).argmin()
    return array[idx][0]

sampler = Sampler(17, None, False)
sampler.datasets = sampler.get_data()[:2]
print(sampler.datasets)
sampler.compute_fourier()
print(sampler.fourier_data)


to_plot = sampler.datasets[0]
print(to_plot)
plt.plot(to_plot.T[1], to_plot.T[0])

t = 0
while t < 1440:
    print(t)
    nearest = find_nearest_time(to_plot, t)
    plt.plot(t, 0, marker="o", markersize=5, markeredgecolor="Black", markerfacecolor="red")
    t += sampler.compute_wait_time(t)

plt.show()

"""




samplers = [Sampler(i, None, True) for i in range(1, 11)]
samplers[1].save = True

loop = asyncio.get_event_loop()
result = loop.run_until_complete(asyncio.wait([i.controler() for i in samplers]))
"""