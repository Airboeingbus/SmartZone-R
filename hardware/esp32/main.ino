/*
 * SmartZone-R: Runway Surface Monitoring System
 * ESP32 Main Code
 * 
 * Reads multiple sensors and displays runway conditions
 * on OLED display and outputs JSON over Serial.
 * 
 * Connections:
 * - DHT22: GPIO 4 (temperature/humidity)
 * - HC-SR04 TRIG: GPIO 5 (ultrasonic trig)
 * - HC-SR04 ECHO: GPIO 18 (ultrasonic echo)
 * - Stress sensor (analog): GPIO 34 (ADC)
 * - LED Green: GPIO 2
 * - LED Yellow: GPIO 15
 * - LED Red: GPIO 16
 * - OLED SDA: GPIO 21
 * - OLED SCL: GPIO 22
 */

#include <DHT.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// ===== PIN DEFINITIONS =====
#define DHT_PIN 4
#define TRIG_PIN 5
#define ECHO_PIN 18
#define STRESS_PIN 34  // ADC pin for stress measurement
#define LED_GREEN 2
#define LED_YELLOW 15
#define LED_RED 16
#define SDA_PIN 21
#define SCL_PIN 22

// ===== CONSTANTS =====
#define DHT_TYPE DHT22
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define ZONE_ID 1  // Single zone for simulation
#define SAMPLE_INTERVAL 10000  // 10 seconds

// ===== GLOBAL OBJECTS =====
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ===== STRUCTURE FOR SENSOR DATA =====
struct SensorData {
  int zone;
  float temperature;
  float humidity;
  float stress;
  float water_depth;  // in mm
  float fod_score;     // FOD (Foreign Object Debris) - random for simulation
  unsigned long timestamp;
};

// ===== THRESHOLDS =====
const float STRESS_THRESHOLD = 70.0;
const float RUBBER_THRESHOLD = 3.0;
const float WATER_THRESHOLD = 10.0;
const float TEMP_CRITICAL_HIGH = 50.0;
const float TEMP_CRITICAL_LOW = 0.0;
const float HUMIDITY_THRESHOLD = 80.0;

// ===== SETUP FUNCTION =====
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize DHT22
  dht.begin();
  
  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 allocation failed");
    while (1);
  }
  
  // Clear display and show startup message
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("SmartZone-R v1.0");
  display.println("Initializing sensors...");
  display.display();
  
  // Initialize LED pins
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Turn off all LEDs initially
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  
  Serial.println("\n=== SmartZone-R Runway Monitor ===");
  Serial.println("System initialized successfully");
  delay(2000);
}

// ===== MAIN LOOP =====
void loop() {
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = millis();
  
  // Sample sensors every SAMPLE_INTERVAL milliseconds
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = currentTime;
    
    // Read sensors
    SensorData data = readAllSensors();
    
    // Determine severity level
    int severeityLevel = calculateSeverity(data);
    
    // Update LED indicators
    updateLEDStatus(severeityLevel);
    
    // Display on OLED
    displayOnOLED(data, severeityLevel);
    
    // Output JSON to Serial
    outputJSON(data);
  }
}

// ===== SENSOR READING FUNCTIONS =====
SensorData readAllSensors() {
  SensorData data;
  data.zone = ZONE_ID;
  data.timestamp = millis();
  
  // Read DHT22 (temperature & humidity)
  data.temperature = dht.readTemperature();
  data.humidity = dht.readHumidity();
  
  // Check if DHT reads are valid
  if (isnan(data.temperature) || isnan(data.humidity)) {
    data.temperature = 25.0;
    data.humidity = 60.0;
  }
  
  // Read HC-SR04 ultrasonic distance sensor (proxy for water depth)
  data.water_depth = readUltrasonicDistance();
  
  // Read stress from analog pin (0-4095, map to 0-100)
  int rawStress = analogRead(STRESS_PIN);
  data.stress = map(rawStress, 0, 4095, 0, 100);
  
  // Simulate FOD (Foreign Object Debris) score randomly
  data.fod_score = random(0, 100) * 0.01;  // 0.0 to 0.99
  
  return data;
}

float readUltrasonicDistance() {
  // Send pulse to trigger pin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Measure the echo time
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // timeout 30ms
  
  // Convert to distance in mm
  // Speed of sound = 343 m/s = 0.343 mm/microsecond
  // Distance = (duration / 2) * 0.343
  float distance = (duration / 2.0) * 0.343;
  
  // Constrain to reasonable range (0-200mm for water depth)
  if (distance < 0 || distance > 200) {
    distance = 0;
  }
  
  return distance;
}

// ===== SEVERITY LEVEL CALCULATION =====
int calculateSeverity(const SensorData& data) {
  int severity = 0;  // 0=Green, 1=Yellow, 2=Red
  
  // High stress
  if (data.stress > STRESS_THRESHOLD) {
    severity = max(severity, 1);
    if (data.stress > 85) severity = 2;
  }
  
  // High humidity
  if (data.humidity > HUMIDITY_THRESHOLD) {
    severity = max(severity, 1);
  }
  
  // Temperature extremes
  if (data.temperature > TEMP_CRITICAL_HIGH || data.temperature < TEMP_CRITICAL_LOW) {
    severity = max(severity, 2);
  }
  
  // Water accumulation
  if (data.water_depth > WATER_THRESHOLD) {
    severity = max(severity, 1);
    if (data.water_depth > 20) severity = 2;
  }
  
  return severity;
}

// ===== LED CONTROL =====
void updateLEDStatus(int severity) {
  // Turn off all LEDs first
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  
  // Set appropriate LED based on severity
  if (severity == 0) {
    digitalWrite(LED_GREEN, HIGH);
  } else if (severity == 1) {
    digitalWrite(LED_YELLOW, HIGH);
  } else if (severity == 2) {
    digitalWrite(LED_RED, HIGH);
  }
}

// ===== OLED DISPLAY =====
void displayOnOLED(const SensorData& data, int severity) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  
  // Title
  display.println("=== SmartZone-R ===");
  display.println("");
  
  // Zone and status
  const char* status_str = (severity == 0) ? "OK" : (severity == 1) ? "CAUTION" : "CRITICAL";
  display.printf("Zone: %d | Status: %s", data.zone, status_str);
  display.println("");
  
  // Temperature & Humidity
  display.printf("Temp: %.1f°C | Hum: %.0f%%", data.temperature, data.humidity);
  display.println("");
  
  // Stress Level
  display.printf("Stress: %.1f%%", data.stress);
  display.println("");
  
  // Water Depth
  display.printf("Water: %.1f mm", data.water_depth);
  display.println("");
  
  // FOD Score
  display.printf("FOD: %.2f", data.fod_score);
  display.println("");
  
  // Timestamp
  display.printf("Time: %lu ms", data.timestamp);
  
  // Send to display
  display.display();
}

// ===== JSON OUTPUT =====
void outputJSON(const SensorData& data) {
  // Create JSON document
  StaticJsonDocument<256> doc;
  
  doc["zone"] = data.zone;
  doc["temp"] = round(data.temperature * 10) / 10.0;      // Round to 1 decimal
  doc["humidity"] = round(data.humidity * 10) / 10.0;      // Round to 1 decimal
  doc["stress"] = round(data.stress * 10) / 10.0;          // Round to 1 decimal
  doc["water_mm"] = round(data.water_depth * 10) / 10.0;   // Round to 1 decimal
  doc["fod"] = round(data.fod_score * 100) / 100.0;        // Round to 2 decimals
  doc["timestamp"] = data.timestamp;
  
  // Serialize and send
  serializeJson(doc, Serial);
  Serial.println();  // Add newline
}

// ===== UTILITY FUNCTIONS =====
float round(float value) {
  return floor(value * 100 + 0.5) / 100.0;
}

int max(int a, int b) {
  return (a > b) ? a : b;
}
