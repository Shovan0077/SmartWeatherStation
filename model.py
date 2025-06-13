import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
import joblib
import os

#CSV file loading
FILE_PATH = 'sensor_log.csv'
if not os.path.exists(FILE_PATH):
    raise FileNotFoundError(f"CSV file not found at {FILE_PATH}")

df = pd.read_csv(FILE_PATH)

# Clean & Prepare
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.dropna(subset=['temperature', 'humidity', 'pressure'])  # Dropping unnecessary rows

# Add seconds since beginning as a time feature
df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

X = df[['time_seconds']]
y = df[['temperature', 'humidity', 'pressure']]

# Train Multi-output Regression Model
print("Training regression model...")
base_model = LinearRegression()
model = MultiOutputRegressor(base_model)
model.fit(X, y)
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Prediction on training data
y_pred = model.predict(X)

#Evaluation using regression metrics
mse = mean_squared_error(y, y_pred, multioutput='raw_values')  
mae = mean_absolute_error(y, y_pred, multioutput='raw_values')
r2 = r2_score(y, y_pred, multioutput='raw_values')

columns = y.columns 
for i, col in enumerate(columns):
    print(f"\n📈 Accuracy metrics for {col}:")
    print(f"  • Mean Squared Error (MSE): {mse[i]:.3f}")
    print(f"  • Mean Absolute Error (MAE): {mae[i]:.3f}")
    print(f"  • R² Score: {r2[i]:.3f}")


#Saving the model
MODEL_FILE = 'weather_model.pkl'
joblib.dump(model, MODEL_FILE)
print(f"Model saved as: {MODEL_FILE}")
