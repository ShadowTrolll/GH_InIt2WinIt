#!/usr/bin/env python3

import requests, json, time, copy
import numpy as np
from enum import Enum

TEAM_NAME = "yomama"

SAMPLING_PERIOD = 5
MINUTES_IN_DAY = 24 * 60
HEADER = {
    "accept" : "application/json",
    "x-token" : TEAM_NAME
}

class SamplerCommand(Enum):
    DO_SAMPLE = 0
    DONT_SAMPLE = 1

class SamplingComander:
    def __init__(self, n_meters, sampling_schedule):
        """
            meter_ids: [1,2,3,4,...]
        """
        assert sampling_schedule.shape[0] == n_meters
        assert sampling_schedule.shape[1] == (MINUTES_IN_DAY // SAMPLING_PERIOD)
        self.n_meters = n_meters
        self.sampling_schedule = sampling_schedule

    def predict_all(self, time):
        predictions = list()
        for meter_i in range(1, self.n_meters + 1):
            predictions.append(self.predict(time, meter_i))
        return predictions

    def predict(self, time, meter_id):
        assert meter_id >= 1 and meter_id <= self.n_meters
        schedule_idx = self.time2idx(time)
        ret = (
            SamplerCommand.DO_SAMPLE
            if self.sampling_schedule[meter_id - 1][schedule_idx]
            else SamplerCommand.DONT_SAMPLE
        )
        return ret

    def time2idx(self, time):
        return time // SAMPLING_PERIOD
    
class Sampler:
    URL_TIME = r"https://greenhack.mymi.cz/time"
    URL_METER = r"https://greenhack.mymi.cz/meter/{meter_id}?ts_from=0"

    def __init__(self):
        pass

    def meter_url(self, meter_id):
        """Modified data request url"""
        return copy.copy(Sampler.URL_METER).format(meter_id = meter_id)
    
    def get_server_response(self, url):
        return requests.get(
            url = url,
            headers = HEADER
        )
    
    def minutes_since_midnight(self):
        server_response = self.get_server_response(Sampler.URL_TIME)
        linux_time = json.loads(
            server_response.text
        )["absolute-time"]
        msm = time.gmtime(linux_time)
        return msm.tm_hour * 60 + msm.tm_min
    
    def get_current_sensor_measurement(self, meter_id):
        url = self.meter_url(meter_id=meter_id)
        server_response = self.get_server_response(url)
        response_json = json.loads(
            server_response.text
        )
        return response_json[-1]["variable_importance"]  # Latest measurement
    
if __name__ == "__main__":
    schedule = np.zeros(MINUTES_IN_DAY // SAMPLING_PERIOD).reshape(1, -1)
    n_meters = schedule.shape[0]
    print(schedule.shape[1])
    sample_commander = SamplingComander(n_meters, schedule)

    t = MINUTES_IN_DAY - 1
    print(sample_commander.predict(t, meter_id = 1))
    print(sample_commander.predict_all(t))

    sampler = Sampler()
    print(sampler.minutes_since_midnight())
    print(sampler.get_current_sensor_measurement(meter_id=10))