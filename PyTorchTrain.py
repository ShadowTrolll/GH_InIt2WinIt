import torch
import torch.nn as nn
import torch.utils.data as data
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import librosa

from nnutils import *
from speechModelPytorch import *


def train(model, device, criterion, optimizer, scheduler, epoch, iter_meter):
    #model.train()
    batch_size = 6
    x, y = torch.load('tensor.pt')
    for k in range(0,len(x),6):
        x_d, y_d = importance.to(x[k:k+batch_size]), time.to(y[k:k+batch_size])

        optimizer.zero_grad()

        output = model(x_d)
        output = F.log_softmax(output, dim=2)
        output = output.transpose(0, 1)

        loss = criterion(output,y_d)
        loss.backward()

        optimizer.step()
        scheduler.step()
        iter_meter.step()

        #torch.nn.utils.clip_grad_value_(model.parameters(), 20)

kwargs = {'num_workers':2, 'pin_memory': True}

model = SpeechModel().to('cuda')
#model.load_state_dict(torch.load('/mnt/LibriSpeech/model.txt'), strict=False)

epochs_num = 10
lr_rate = 0.0002

optimizer = optim.AdamW(model.parameters(), lr_rate)
criterion = nn.MSELoss().to('cuda')
scheduler = optim.lr_scheduler.OneCycleLR(optimizer, max_lr=lr_rate,
                                        steps_per_epoch=int(len(train_loader)),
                                        epochs=epochs_num,
                                        anneal_strategy='linear')
#using dynamic learning rate to prevent gradient explosion


iter_meter = IterMeter()
for epoch in range(1, epochs_num +1):
    train(model, 'cuda', criterion, optimizer, scheduler, epoch, iter_meter)
    torch.save(model.state_dict(),'')

