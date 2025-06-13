SMART WEATHER STATION & FORECASTING

HARDWARE:- ESP32, DHT11, BMP180, RAIN SENSOR, LDR SENSOR, CONNECTING WIRES, BREADBOARD
CORE-STACK:- ARDUINO IDE, PYTHON, FLASK, CSV, HTML,CSS
LIBRARIES USED:- pandas, numpy, sklearn.linear_model.LinearRegression, sklearn.multioutput.MultiOutputRegressor, joblib, datetime, datetime.timedelta, os

WORKFLOW OF THE PROJECT :-

Step 1: Environmental Weather Data Collection via Sensors.

Step 2: ESP32 reads the sensor data and formats it into JSON structure. 

Step 3: ESP32 sends the data to Flask server(backend) via WiFi.

Step 4: Flask server logs the data into a CSV file with respective timestamps.

Step 5: Machine Learning based Regression Model using the logged data predicts future weather parameters.

Step 6: Forecasted data is served through API endpoints.

Step 7: Real-time Weather Data along with Forecasted Data is displayed on the Dashboard





THANK YOU:)
