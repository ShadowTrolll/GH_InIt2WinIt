#!/usr/bin/env python3

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