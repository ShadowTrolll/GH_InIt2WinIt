import pickle
import torch
import data_prompts

with open('data.pickle', 'rb') as handle:
    data = pickle.load(handle)


x
for num,d in enumerate(data):
    if num > len(data)*0.9:
        break
    else:


