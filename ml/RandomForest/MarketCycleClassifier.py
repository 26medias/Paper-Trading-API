import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import numpy as np

class MarketCycleClassifier:
    def __init__(self, data_dir, model_dir, n_estimators=100, test_size=0.2, val_size=0.1, random_state=42):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.n_estimators = n_estimators
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.model = RandomForestClassifier(n_estimators=self.n_estimators, random_state=self.random_state)
        
    def load_data(self):
        all_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        df_list = [pd.read_csv(file) for file in all_files]
        self.data = pd.concat(df_list, ignore_index=True)
        print(f"Data loaded. Shape: {self.data.shape}")
        
    def preprocess_data(self):
        # Debug print: show first few rows of the data
        print("First 5 rows of data before preprocessing:")
        print(self.data.head())

        # Ensure all data is numeric
        self.data.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Debug print: check for NaN values before dropping them
        if self.data.isnull().values.any():
            print("Data contains NaN values before dropping them.")

        self.data.dropna(inplace=True)

        # Debug print: show first few rows of the data after dropping NaNs
        print("First 5 rows of data after dropping NaNs:")
        print(self.data.head())

        # Convert the label to integer
        print("Unique values in label column before conversion:", self.data['label'].unique())
        self.data['label'] = self.data['label'].astype(int)
        print("Unique values in label column after conversion:", self.data['label'].unique())

        self.X = self.data.drop(columns=['label'])
        self.y = self.data['label']
        
        # Debug prints
        print(f"After preprocessing, data shape: {self.data.shape}")
        print(f"X shape: {self.X.shape}, y shape: {self.y.shape}")
        print(f"First 5 rows of X:\n{self.X.head()}")
        print(f"First 5 rows of y:\n{self.y.head()}")
        
        # Check for NaN or infinite values
        if self.X.isnull().values.any() or self.y.isnull().values.any():
            raise ValueError("NaN values found in the dataset.")
        if np.isinf(self.X.values).any() or np.isinf(self.y.values).any():
            raise ValueError("Infinite values found in the dataset.")
        
    def split_data(self):
        X_train, X_temp, y_train, y_temp = train_test_split(
            self.X, self.y, test_size=self.test_size + self.val_size, random_state=self.random_state, stratify=self.y)
        
        val_test_ratio = self.val_size / (self.test_size + self.val_size)
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            X_temp, y_temp, test_size=1 - val_test_ratio, random_state=self.random_state, stratify=y_temp)
        
        self.X_train, self.y_train = X_train, y_train
        
        # Debug prints
        print(f"Training set shape: {self.X_train.shape}")
        print(f"Validation set shape: {self.X_val.shape}")
        print(f"Test set shape: {self.X_test.shape}")
        
    def train_model(self):
        self.model.fit(self.X_train, self.y_train)
        
    def evaluate_model(self):
        y_train_pred = self.model.predict(self.X_train)
        y_val_pred = self.model.predict(self.X_val)
        y_test_pred = self.model.predict(self.X_test)
        
        print("Training Accuracy:", accuracy_score(self.y_train, y_train_pred))
        print("Validation Accuracy:", accuracy_score(self.y_val, y_val_pred))
        print("Test Accuracy:", accuracy_score(self.y_test, y_test_pred))
        
        print("Validation Classification Report:")
        print(classification_report(self.y_val, y_val_pred))
        
        print("Test Classification Report:")
        print(classification_report(self.y_test, y_test_pred))
        
        # Confusion matrices
        print("Validation Confusion Matrix:")
        print(confusion_matrix(self.y_val, y_val_pred))
        
        print("Test Confusion Matrix:")
        print(confusion_matrix(self.y_test, y_test_pred))
        
    def save_model(self):
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, "market_cycle_classifier.joblib")
        joblib.dump(self.model, model_path)
        
    def load_model(self, model_path):
        self.model = joblib.load(model_path)
        
    def run(self):
        self.load_data()
        self.preprocess_data()
        self.split_data()
        self.train_model()
        self.evaluate_model()
        self.save_model()