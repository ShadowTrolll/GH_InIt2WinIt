#!/usr/bin/env python3

import requests, json, time, copy, scipy
import numpy as np
import matplotlib.pyplot as plt
from data_sampler import HEADER

URL_ALL = "https://greenhack.mymi.cz/meter"
URL_ONE = r"https://greenhack.mymi.cz/meter/{meter_id}?ts_from=0"

def create_dataset(meter_id, one_day = True):
    """
        dataset = [
            (importance_1, time_in_minutes_1),
            (importance_2, time_in_minutes_2),
            (importance_3, time_in_minutes_3),
            ...
        ]
    """
    assert isinstance(meter_id, int)
    data_points, dataset, datasets = [], [], []
    data = get_meter_data(meter_id)
    for data_point in data:
        data_points.append(
            (data_point["variable_importance"], time2minute(data_point["time"]))
        )
    
    data_points = np.array(data_points)
    dataset_diff = np.diff(data_points[:,1])
    idxs, = np.where(dataset_diff <= 0)
    for i in range(0, len(idxs)):
        if i + 1 != len(idxs):
            dataset = data_points[idxs[i]+1:idxs[i+1]+1, :]
        else:
            dataset = data_points[idxs[i]+1:0, :]
            
        if dataset.shape[0] != 0:
            datasets.append(dataset)
        
    if one_day:
        return datasets[0]
    return datasets

def get_meter_data(meter_id):
    assert isinstance(meter_id, int)
    static_importance = json.loads(
        requests.get(URL_ALL, headers=HEADER).text
    )[meter_id - 1]["static_importance"]
    print("Getting json")
    url = copy.copy(URL_ONE).format(meter_id = meter_id)
    response = requests.get(url, headers=HEADER)
    data = json.loads(response.text)
    for i in range(len(data)):
        data[i]["variable_importance"] *= static_importance
    return data

def time2minute(linux_time):
    t = time.gmtime(linux_time)
    m = t.tm_hour * 60 + t.tm_min
    return m 

def average_day(meter_dataset):
    avg_day = np.zeros_like(meter_dataset[0])
    for i in range(len(meter_dataset)):
        avg_day += meter_dataset[i]
    avg_day = avg_day / len(meter_dataset)
    avg_day[:,0] = scipy.signal.medfilt(avg_day[:,0], kernel_size=7)
    return avg_day

def plot_day(day):
    t = day[:, 1]
    imp = day[:, 0]
    plt.plot(t, imp)
    plt.show()

def optimize_schedule(day):
    t, imp = day[:, 1], day[:, 0]
    unique_vals = np.unique(imp)

    L = 0.4

    def reward(dec_boundary, imp_array):
        r = 0.0
        for i in range(len(imp_array)):
            importance = imp_array[i]
            r += (importance - L) if importance >= dec_boundary else 0.0
        return r
    
    def schedule_gen(dec_boundary, imp_array):
        return imp_array >= dec_boundary
    
    best_db, best_reward = None, None
    for current_db in unique_vals:
        r = reward(
            dec_boundary=current_db,
            imp_array=imp
        )
        if best_reward is None or best_reward < r:
            best_db, best_reward = current_db, r

    return best_db, best_reward, schedule_gen(best_db, imp_array=imp)

if __name__ == "__main__":

    SCHEDULE_FILE = "schedule.npy"

    out_np = np.load(SCHEDULE_FILE)

    for meter_id in range(1, 1000 + 1):
        if not np.isnan(out_np[meter_id - 1][0]):
            continue
        print("Testing meter ID:", meter_id)
        try:
            meter_dataset = create_dataset(meter_id=meter_id, one_day=False)
            # print("Number of unique days:", len(meter_dataset))

            avg_day = average_day(meter_dataset=meter_dataset)
            # print("Unique importance values in average day:", np.unique(avg_day[:,0]))

            best_db, best_reward, sampling_schedule = optimize_schedule(avg_day)
            # print("Decision boundary:", best_db)
            # print("Reward:", best_reward)
            # plot_day(avg_day)
            out_np[meter_id - 1] = sampling_schedule
        except KeyError:
            print("Key error")

    np.save(SCHEDULE_FILE, out_np)