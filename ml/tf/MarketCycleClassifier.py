import os
import glob
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import tensorflowjs as tfjs

class MarketCycleClassifierTF:
    def __init__(self, data_dir=None, model_dir=None, test_size=0.2, val_size=0.1, random_state=42, model="up", epochs=20, batch_size=32):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.modelName = model
        self.epochs = epochs
        self.batch_size = batch_size
        
    def load_data(self):
        all_files = glob.glob(os.path.join(self.data_dir, f"{self.modelName}_*.csv"))
        df_list = [pd.read_csv(file) for file in all_files]
        self.data = pd.concat(df_list, ignore_index=True)
        print(f"Data loaded. Shape: {self.data.shape}")
        
    def preprocess_data(self):
        print("First 5 rows of data before preprocessing:")
        print(self.data.head())

        self.data.replace([np.inf, -np.inf], np.nan, inplace=True)
        if self.data.isnull().values.any():
            print("Data contains NaN values before dropping them.")
        self.data.dropna(inplace=True)

        print("First 5 rows of data after dropping NaNs:")
        print(self.data.head())

        self.data['label'] = self.data['label'].astype(int)

        self.X = self.data.drop(columns=['label'])
        self.y = self.data['label']
        
        print(f"After preprocessing, data shape: {self.data.shape}")
        print(f"X shape: {self.X.shape}, y shape: {self.y.shape}")
        print(f"First 5 rows of X:\n{self.X.head()}")
        print(f"First 5 rows of y:\n{self.y.head()}")
        
        if self.X.isnull().values.any() or self.y.isnull().values.any():
            raise ValueError("NaN values found in the dataset.")
        if np.isinf(self.X.values).any() or np.isinf(self.y.values).any():
            raise ValueError("Infinite values found in the dataset.")
        
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(self.X)
        
    def split_data(self):
        X_train, X_temp, y_train, y_temp = train_test_split(
            self.X, self.y, test_size=self.test_size + self.val_size, random_state=self.random_state, stratify=self.y)
        
        val_test_ratio = self.val_size / (self.test_size + self.val_size)
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            X_temp, y_temp, test_size=1 - val_test_ratio, random_state=self.random_state, stratify=y_temp)
        
        self.X_train, self.y_train = X_train, y_train
        
        print(f"Training set shape: {self.X_train.shape}")
        print(f"Validation set shape: {self.X_val.shape}")
        print(f"Test set shape: {self.X_test.shape}")
        
    def build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(self.X.shape[1],)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model = model
        
    def train_model(self):
        self.model.fit(self.X_train, self.y_train, epochs=self.epochs, batch_size=self.batch_size, validation_data=(self.X_val, self.y_val))
        
    def evaluate_model(self):
        train_loss, train_acc = self.model.evaluate(self.X_train, self.y_train, verbose=0)
        val_loss, val_acc = self.model.evaluate(self.X_val, self.y_val, verbose=0)
        test_loss, test_acc = self.model.evaluate(self.X_test, self.y_test, verbose=0)
        
        print("Training Accuracy:", train_acc)
        print("Validation Accuracy:", val_acc)
        print("Test Accuracy:", test_acc)
        
    def save_model(self):
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, f"tf_model_{self.modelName}.keras")
        self.model.save(model_path)
        
        # Save the scaler
        scaler_path = os.path.join(self.model_dir, f"scaler_{self.modelName}.pkl")
        joblib.dump(self.scaler, scaler_path)
        
    def load_model(self):
        model_path = os.path.join(self.model_dir, f"tf_model_{self.modelName}.keras")
        self.model = tf.keras.models.load_model(model_path)
        
        # Load the scaler
        scaler_path = os.path.join(self.model_dir, f"scaler_{self.modelName}.pkl")
        self.scaler = joblib.load(scaler_path)
        
    def predict(self, input_data):
        input_df = pd.DataFrame([input_data])
        input_scaled = self.scaler.transform(input_df)
        prediction = self.model.predict(input_scaled)
        return prediction[0]
    
    def export_model_to_js(self):
        model_path = os.path.join(self.model_dir, f"tf_model_{self.modelName}.keras")
        tfjs_target_dir = os.path.join(self.model_dir, f"tfjs_model_{self.modelName}")
        os.makedirs(tfjs_target_dir, exist_ok=True)
        tfjs.converters.save_keras_model(self.model, tfjs_target_dir)
        
    def run(self):
        self.load_data()
        self.preprocess_data()
        self.split_data()
        self.build_model()
        self.train_model()
        self.evaluate_model()
        self.save_model()
        self.export_model_to_js()
