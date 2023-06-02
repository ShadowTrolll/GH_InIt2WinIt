#!/usr/bin/env python3

import time
import requests
import json

URL = "https://greenhack.mymi.cz/meter"
HEADER = {
    "accept": r"application/json",
    "x-token": "yomama"
}

def get_meter_data():
    response = requests.get(URL, headers=HEADER)
    data = json.loads(response.text)
    return data

def time2minute(linux_time):
    t = time.gmtime(linux_time)
    m = t.tm_hour * 60 + t.tm_min
    return m 