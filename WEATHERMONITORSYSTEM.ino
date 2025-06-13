#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_BMP085.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "Connect";
const char* password = "mastershovan";

// Flask server IP and port
const char* serverURL = "http://192.168.242.179:5000/upload";

// Sensor pins
#define DHTPIN 4
#define DHTTYPE DHT11
#define LDR_PIN 34
#define RAIN_PIN 35

// Sensor objects
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;

bool wifiConnected = false;

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
  } else {
    wifiConnected = false;
    Serial.println("\n Failed! Check WiFi credentials or router.");
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  if (!bmp.begin()) {
    Serial.println("BMP180 not found");
    while (1);
  }

  connectToWiFi();
}

void loop() {
  if (!wifiConnected || WiFi.status() != WL_CONNECTED) {
    Serial.println("Disconnected WiFi.... Trying to reconnect...");
    connectToWiFi();

    if (!wifiConnected) {
      delay(10000); // delay before next attempt
      return;
    }
  }

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  float pressure = bmp.readPressure() / 100.0;  // Pa to hPa
  int ldrValue = analogRead(LDR_PIN);
  int rainValue = analogRead(RAIN_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor.");
    delay(2000);
    return;
  }

  // Sensor readings printing
  Serial.printf(" Temp: %.2f °C | Humidity: %.2f %% | Pressure: %.2f hPa | LDR: %d | Rain: %d\n",
                temperature, humidity, pressure, ldrValue, rainValue);

  // SEnding to Flask Server
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  String json = "{\"temperature\":" + String(temperature, 2) +
                ",\"humidity\":" + String(humidity, 2) +
                ",\"pressure\":" + String(pressure, 2) +
                ",\"ldr\":" + String(ldrValue) +
                ",\"rain\":" + String(rainValue) + "}";

  Serial.println("📡 Sending data...");
  Serial.println("Payload: " + json);

  int responseCode = http.POST(json);

  if (responseCode > 0) {
    Serial.println("Server response: " + http.getString());
  } else {
    Serial.println("POST failed, error code: " + String(responseCode));
  }

  http.end();
  delay(10000); // delay of 10 secs
}
