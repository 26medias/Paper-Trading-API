import os
import glob
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.onnx
from torch.utils.data import DataLoader, Dataset, random_split
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class MarketCycleDataset(Dataset):
    def __init__(self, data_files):
        self.data = []
        for file in data_files:
            df = pd.read_csv(file)
            print(f"Loaded {file} with shape {df.shape}")
            self.data.append(df.values)
        self.data = np.vstack(self.data)
        print(f"Stacked data shape: {self.data.shape}")

        # Normalize features to [0, 1]
        scaler = MinMaxScaler()
        self.features = torch.tensor(scaler.fit_transform(self.data[:, :-1].astype(np.float32)), dtype=torch.float32)
        print(f"Features tensor shape: {self.features.shape}")

        # Convert labels to 0 and 1
        self.labels = torch.tensor([1 if label else 0 for label in self.data[:, -1]], dtype=torch.long)
        print(f"Labels tensor shape: {self.labels.shape}")

    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        features = self.features[idx].reshape(4, 4)
        return features, self.labels[idx]

class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(16, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class MarketCycleClassifier:
    def __init__(self, data_dir, model_dir, model):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.model_name = model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_data(self):
        all_files = glob.glob(os.path.join(self.data_dir, f"{self.model_name}_*.csv"))
        dataset = MarketCycleDataset(all_files)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        self.train_dataset, self.val_dataset = random_split(dataset, [train_size, val_size])
        self.train_loader = DataLoader(self.train_dataset, batch_size=32, shuffle=True)
        self.val_loader = DataLoader(self.val_dataset, batch_size=32, shuffle=False)
    
    def train_model(self):
        self.model = SimpleNN().to(self.device)
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        num_epochs = 20
        best_val_loss = float('inf')

        for epoch in range(num_epochs):
            self.model.train()
            running_loss = 0.0
            for features, labels in self.train_loader:
                features, labels = features.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(features).squeeze(1)
                loss = criterion(outputs, labels.float())
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
            avg_train_loss = running_loss / len(self.train_loader)
            
            val_loss = self.evaluate_model()
            print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            # Save the best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model()

    def evaluate_model(self):
        self.model.eval()
        running_loss = 0.0
        criterion = nn.BCEWithLogitsLoss()
        with torch.no_grad():
            for features, labels in self.val_loader:
                features, labels = features.to(self.device), labels.to(self.device)
                outputs = self.model(features).squeeze(1)
                loss = criterion(outputs, labels.float())
                running_loss += loss.item()
        return running_loss / len(self.val_loader)
    
    def save_model(self):
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, f"{self.model_name}_model.pth")
        torch.save(self.model.state_dict(), model_path)
        
        onnx_path = os.path.join(self.model_dir, f"{self.model_name}_model.onnx")
        dummy_input = torch.randn(1, 4, 4, device=self.device)
        torch.onnx.export(self.model, dummy_input, onnx_path, input_names=['input'], output_names=['output'])
        print(f"Model saved in {model_path} and {onnx_path}")
    
    def run(self):
        self.load_data()
        self.train_model()
