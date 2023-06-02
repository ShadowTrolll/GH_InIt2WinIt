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
    def __init__(self, meter_id, meter_type, importance, time, availability):
        self.meter_id = meter_id
        self.meter_type = meter_type
        self.importance = importance 
        self.time = time
        self.availability = availability

def create_dataset(meter_id = None, one_day = True):
    """
        dataset = [
            (importance_1, time_in_minutes_1),
            (importance_2, time_in_minutes_2),
            (importance_3, time_in_minutes_3),
            ...
        ]
    """
    dataset = []
    if meter_id is not None:
        assert isinstance(meter_id, int)
        data = get_meter_data(meter_id)
        for data_point in data:
            dataset.append(
                (data_point["variable_importance"], time2minute(data_point["time"]))
            )
    else:
        raise NotImplementedError
       
    
    dataset = np.array(dataset)
    if one_day:
        dataset_diff = np.diff(dataset[:,1])
        idxs, = np.where(dataset_diff <= 0)
        dataset = dataset[idxs[0]+1:idxs[1]+1, :]
        
    return dataset

def get_meter_data(meter_id = None):
    response = None
    if meter_id is not None:
        assert isinstance(meter_id, int)
        url = copy.copy(URL_ONE).format(meter_id = meter_id)
    else:
        url = URL_ALL
    response = requests.get(url, headers=HEADER)
    data = json.loads(response.text)
    return data

def time2minute(linux_time):
    t = time.gmtime(linux_time)
    m = t.tm_hour * 60 + t.tm_min
    return m 

<<<<<<< HEAD
def all_data(): 
    data = []
    for meter in get_meter_data():
        print('next')
        for data_meter in get_meter_data(meter['meter_id']):
            if 'status' not in data_meter:
                data.append(MeterTimeSample(
                        meter['meter_id'],
                        meter['meter_type'],
                        float(data_meter['variable_importance']),
                        time2minute(data_meter['time']),
                        data_meter['availability'])
                    )

    print(data)
    with open('data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

all_data()
#print(get_meter_data(100))
=======
print(get_meter_data(4))
>>>>>>> c3f8bd581a5ab7905dfee62f81a108908b86d0b1
