import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
import numpy as np
from model import ISLModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "models", "isl_model.pth")
labels_path = os.path.join(BASE_DIR, "..", "models", "labels_integers.pth")

model = ISLModel()
weights = torch.load(model_path)
model.load_state_dict(weights)
model.eval() #switching to evaluation mode - Dropout is disabled

#key - labels, value - integers
labels_integers = torch.load(labels_path)

#key - integers, value - labels
integers_labels = {value : key for key,value in  labels_integers.items()}


def predict_sign(d) -> str:
    #converting incoming list data into numpy array and then into tensor
    data = np.array(d)
    data_x = torch.tensor(data, dtype = torch.float32) #(126,)
    data_x = torch.unsqueeze(data_x,0) #(1,126)

    with torch.no_grad():
       output = model(data_x)
       prediction = torch.argmax(output, dim = 1) #(1,)
       return integers_labels[prediction[0].item()] #string returned


