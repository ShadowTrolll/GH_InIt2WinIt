import pickle
import torch
import data_prompts
from data_prompts import MeterTimeSample

with open('data.pickle', 'rb') as handle:
    data = pickle.load(handle)

x = []
y = []

for num,d in enumerate(data):
    if num > len(data)*0.9:
        break
    elif d.availability:
        x.append([d.meter_id, d.static_importance, d.time])
        y.append([d.static_importance*d.importance])

x = torch.tensor(x)
y = torch.tensor(y)
torch.save((x,y), 'tensor.pt')

