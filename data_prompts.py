#!/usr/bin/env python3

import numpy as np
import copy
import time
import requests
import json
from scipy.fft import fft, ifft
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

def plot_datasets(dataset):
    for i in range(len(dataset)):
        day_i = dataset[i]
        t = day_i[:,1]
        i = day_i[:,0]
        
        plt.plot(t,i)
        
def plot_day(day):
    t = day[:,1]
    i = day[:,0]
    plt.plot(t,i)
    
def average_day(dataset):
    day_result = np.zeros_like(dataset[0])
    for i in range(len(dataset)):
        day_i = dataset[i]
        day_result += day_i
    return day_result / len(dataset)

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
    if not data:
        return None

    for data_point in data:
        data_points.append(
            (data_point["variable_importance"], time2minute(data_point["time"]))
        )
    
    #print(data_points)
    data_points = np.array(data_points)
    dataset_diff = np.diff(data_points[:,1])
    idxs, = np.where(dataset_diff <= 0)
    #print("Idxs", idxs, len(data_points))
    for i in range(len(idxs)):
        if i + 1 != len(idxs):
            #print("ids1", idxs[i]+1, idxs[i+1]+1)
            dataset = data_points[idxs[i]+1:idxs[i+1]+1, :]
        else:
            #print("ids2", idxs[i]+1, 0)
            dataset = data_points[idxs[i]+1:len(data_points), :]
            #print("dss", dataset.shape)
            
        if dataset.shape[0] != 0:
            datasets.append(dataset)
    #dataset = data_points[idxs[-1]+1:len(data_points), :]
    #if dataset.shape[0] != 0:
    #    datasets.append(dataset)

    if one_day:
        return datasets[0]
    return datasets

def meter_fft(datasets):
    if not datasets:
        return None

    avg_day = average_day(datasets)
    filtered = []
    for day in datasets:
        x = fft(day[:,0])

        N = 8
        K = 150

        x[N:K] = 0
        x[-K:-N] = 0

        filtered.append(ifft(x))

    filtered_avg = average_day(filtered)
    #plot_day(avg_day)
    #plt.plot(day[:,1],abs(filtered_avg))
    #plt.show()
    return [avg_day[:,1],abs(filtered_avg)]

def get_meter_data(meter_id):
    assert isinstance(meter_id, int)
    try:
        json_data = requests.get(URL_ALL, headers=HEADER).text
    except:
        print("ERROR from", meter_id)
        return None
    static_importance_json = json.loads(json_data)
    static_importance = static_importance_json[meter_id - 1]["static_importance"]
    url = copy.copy(URL_ONE).format(meter_id = meter_id)
    response = requests.get(url, headers=HEADER)
    data = json.loads(response.text)
    if 'status' in data:
        return None

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

if __name__ == "__main__":
    #print(get_meter_data(1))
    print(meter_fft(900))

    #for i in range(0,1000i)