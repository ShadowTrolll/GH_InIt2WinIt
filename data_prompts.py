#!/usr/bin/env python3

import numpy as np
import copy
import time
import requests
import json
import pickle

URL_ALL = "https://greenhack.mymi.cz/meter"
URL_ONE = r"https://greenhack.mymi.cz/meter/{meter_id}?ts_from=0"

HEADER = {
    "accept": r"application/json",
    "x-token": "yomama"
}

class MeterTimeSample:
    def __init__(self, meter_id, static_importance, importance, time, availability):
        self.meter_id = meter_id
        self.static_importance = static_importance
        self.importance = importance 
        self.time = time
        self.availability = availability

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

def previous_datapoints(dataset, time, n_prev = 80):
    assert isinstance(time, int)
    assert time > dataset[0,1]
    assert time > 0 and time < 24 * 60 + 1
    time_copy = dataset[:,1].copy()
    time_diff = time_copy - time
    time_diff, = np.where(time_diff < 0)
    time_idx = time_diff[-1]
    
    ret = np.zeros((n_prev, 2))
    if time_idx >= n_prev:
        ret[:,:] = dataset[time_idx:time_idx - n_prev: -1]
    else:
        ret[0:time_idx + 1] = np.vstack(
            (dataset[time_idx:0: -1], dataset[0])
        )
        for j in range(time_idx + 1, n_prev):
            ret[j] = dataset[0]
    return ret

def get_meter_data(meter_id):
    assert isinstance(meter_id, int)
    static_importance = json.loads(
        requests.get(URL_ALL, headers=HEADER).text
    )[meter_id - 1]["static_importance"]
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

def all_data(): 
    data = []
    for meter in get_meter_data():
        print('next')
        for data_meter in get_meter_data(meter['meter_id']):
            if 'status' not in data_meter:
                data.append(MeterTimeSample(
                        meter['meter_id'],
                        meter['static_importance'],
                        float(data_meter['variable_importance']),
                        time2minute(data_meter['time']),
                        data_meter['availability'])
                    )

    print(data)
    with open('data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

all_data()
#print(get_meter_data(100))
print(get_meter_data(4))
=======
if __name__ == "__main__":
    print(get_meter_data(1))
