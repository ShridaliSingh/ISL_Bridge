import torch
from train_data import ISLModel

model = ISLModel()
weights = torch.load("../models/isl_model.pth")
model.load_state_dict(weights)
model.eval()

#key - labels, value - integers
labels_integers = torch.load("../models/labels_integers.pth")

#key - integers, value - labels
integers_labels = {value : key for key,value in  labels_integers.items()}


def predict_sign(d) -> str:
    #converting incoming numpy array data into tensor
    data_x = torch.tensor(d, dtype = torch.float32) #(126,)
    data_x = torch.unsqueeze(data_x,0) #(1,126)

    with torch.no_grad():
       output = model (data_x)
       prediction = torch.argmax(output, dim = 1) #(1,)
       return integers_labels[prediction[0].item()] #string returned


