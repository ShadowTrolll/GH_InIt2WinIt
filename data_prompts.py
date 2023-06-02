#!/usr/bin/env python3

import copy
import time
import requests
import json

URL_ALL = "https://greenhack.mymi.cz/meter"
URL_ONE = r"https://greenhack.mymi.cz/meter/{meter_id}?ts_from=0"

HEADER = {
    "accept": r"application/json",
    "x-token": "yomama"
}

class meauserement:
    def __init__(self, meter_id, meter_type, importance, time):
        self.meter_id = meter_id
        self.meter_type = meter_type
        self.importance = importance 
        self.time = time

def create_dataset(meter_id = None):
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
                (data_point["importance"], time2minute(data_point["time"]))
            )
    else:
        raise NotImplementedError
    return dataset

def get_meter_data(meter_id = None):
    response = None
    if meter_id is not None:
        assert isinstance(meter_id, int)
        url = copy.copy(URL_ONE).format(meter_id = meter_id)
        print(url)
    else:
        url = URL_ALL
    response = requests.get(url, headers=HEADER)
    data = json.loads(response.text)
    return data

def time2minute(linux_time):
    t = time.gmtime(linux_time)
    m = t.tm_hour * 60 + t.tm_min
    return m 

print(get_meter_data(4))
