from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime, csv, os
import pandas as pd
import numpy as np
import joblib
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# File and model paths
LOG_FILE = 'sensor_log.csv'
FIELDS = ['timestamp', 'temperature', 'humidity', 'pressure', 'ldr', 'rain']
REALTIME_MODEL_PATH = 'temp_predictor.joblib'
FORECAST_MODEL_PATH = 'weather_model.pkl'

# Create log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)

# Load real-time model (for predicting current temp)
try:
    realtime_model = joblib.load(REALTIME_MODEL_PATH)
except:
    realtime_model = None

# Load forecast model (for next 1 hour)
try:
    forecast_model = joblib.load(FORECAST_MODEL_PATH)
except:
    forecast_model = None

def classify_weather(row):
    rain = row['rain']
    ldr = row['ldr']

    if rain < 1500 and ldr > 2500:
        return "⛈️ Heavy Rain"
    elif rain < 1500:
        return "🌧️ Light Rain"
    elif ldr < 1800:
        return "☀️ Sunny"
    elif ldr < 3000:
        return "⛅ Partly Cloudy"
    else:
        return "☁️ Cloudy"


@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    data['timestamp'] = datetime.datetime.now().isoformat()

    # Save to CSV
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data['timestamp'], data['temperature'], data['humidity'],
            data['pressure'], data['ldr'], data['rain']
        ])

    # Predict current temperature using model
    if realtime_model:
        X = [[data['humidity'], data['pressure'], data['ldr'], data['rain']]]
        predicted = realtime_model.predict(X)[0]
        data['predicted_temp'] = round(predicted, 2)
    else:
        data['predicted_temp'] = None

    return jsonify(data)

@app.route('/latest', methods=['GET'])
def latest():
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            last = lines[-1].strip().split(',')
            return jsonify({
                "timestamp": last[0],
                "temperature": float(last[1]),
                "humidity": float(last[2]),
                "pressure": float(last[3]),
                "ldr": int(last[4]),
                "rain": int(last[5])
            })
    except:
        return jsonify({"error": "No data yet"}), 404

@app.route('/forecast', methods=['GET'])
def forecast():
    try:
        if not forecast_model:
            return jsonify({"error": "Forecast model not loaded"}), 500

        df = pd.read_csv(LOG_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

        latest_time = df['timestamp'].max()
        base_time = df['time_seconds'].iloc[-1]

        # Predict for next hour (every 10 mins = 600s)
        future_seconds = np.arange(base_time + 600, base_time + 3600 + 1, 600).reshape(-1, 1)
        predictions = forecast_model.predict(future_seconds)

        forecast_data = []
        for i, (temp, hum, pres) in enumerate(predictions):
            t = latest_time + timedelta(seconds=(i + 1) * 600)
            forecast_data.append({
                "time": t.strftime('%H:%M'),
                "temperature": round(temp, 2),
                "humidity": round(hum, 2),
                "pressure": round(pres, 2)
            })

        # Determine current weather condition
        condition = classify_weather(df.iloc[-1])

        return jsonify({
            "forecast": forecast_data,
            "condition": condition
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
