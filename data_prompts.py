#!/usr/bin/env python3

import time
import requests
import json

URL_ALL = "https://greenhack.mymi.cz/meter"
URL_ONE = r"https://greenhack.mymi.cz/meter/{meter_id}?ts_from=0"

HEADER = {
    "accept": r"application/json",
    "x-token": "yomama"
}

def get_meter_data(meter_id = None):
    response = None
    if meter_id is not None:
        assert isinstance(meter_id, int)
        url = URL_ONE.format(meter_id = meter_id)
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