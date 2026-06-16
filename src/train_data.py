import csv 
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import time

#defining model
class ISLModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(126,256) #(in,out)
        self.fc2 = nn.Linear(256,128)
        self.fc3 = nn.Linear(128,64)
        self.fc4 = nn.Linear(64,33)
    
    def forward(self,x):
        x = self.fc1(x) #input went in thru input layer
        x = nn.functional.relu(x)
        x = self.fc2(x)
        x = nn.functional.relu(x)
        x = self.fc3(x)
        x = nn.functional.relu(x)
        x = self.fc4(x) #out thru the output layer
        return x

def main():
    #X
    dataset = []
    #y (needed to be converted to integer later for network training)
    labels = []
    with open("../data/landmarks_own.csv", "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[-1] != 'sign':
                #126 coordinates and 1 sign, total 127 elements in each row
                dataset.append([float(x) for x in row[0:126]])
                labels.append(row[126])
    
    #dictionary with keys as unique labels and integers as values
    labels_integers = {label : i for i, label in enumerate(sorted(set(labels)))}

    torch.save(labels_integers, "../models/labels_integers.pth")

    #y (integer list)
    labels_ml = [int(labels_integers[x]) for x in labels]
        
    #dataset as numpy array , size (13244, 126)
    X = np.array(dataset, dtype = np.float32)

    #labels(as integers) as numpy array , size  (13244,)
    y = np.array(labels_ml, dtype = np.int64)

    #split dataset for training and testing (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train = torch.tensor(X_train, dtype = torch.float32)
    X_test = torch.tensor(X_test, dtype = torch.float32)
    y_train = torch.tensor(y_train, dtype = torch.long)
    y_test =  torch.tensor(y_test, dtype = torch.long)

    #Datasets
    dataset_train = TensorDataset(X_train,y_train)
    dataset_test = TensorDataset(X_test,y_test)

    #provides data in batches
    train_loader = DataLoader(dataset_train, batch_size = 32, shuffle = True)
    test_loader = DataLoader(dataset_test, batch_size = 32, shuffle = False)

    #initializing model, loss fxn and optimizer
    model = ISLModel()
    loss_fxn = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr = 0.001)

    start = time.time()
    #training loop of 100 epoch
    for _ in range(100):
        total_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            predictions = model(X_batch) #forward pass
            loss = loss_fxn(predictions, y_batch)
            total_loss += loss.item()
            loss.backward()
            optimizer.step() 
        #average loss per epoch
        avg_loss = total_loss / len(train_loader)
        if _ % 10 == 0 :
            print(f"{_} Loss : {avg_loss}")

    print(f"Training time: {(time.time() - start)/ 60 :.2f} minutes") 

    torch.save(model.state_dict(), "../models/isl_model.pth")

    with torch.no_grad():
        correct = 0
        for X_batch , y_batch in test_loader:
            output = model(X_batch) # size - (batch,33) , this calls forward fxn of the class
            predictions = torch.argmax(output, dim = 1) # size - (batch,)
            correct += torch.sum(predictions == y_batch).item()

    accuracy = correct / len(y_test)
    print(f"Accuracy : {accuracy * 100 :.2f} %" )

    

if __name__=="__main__":
    main()