#include <ESP8266WiFi.h>

// Wi-Fi credentials
const char* ssid = "ColdPalmer"; // Replace with your Wi-Fi SSID
const char* password = "david4567"; // Replace with your Wi-Fi password

// Pin for the vibration motor
const int vibrationMotorPin = A0; // D1 on NodeMCU

// Wi-Fi server
WiFiServer server(80);

void setup() {
  // Set motor pin as output
  pinMode(vibrationMotorPin, OUTPUT);
  digitalWrite(vibrationMotorPin, LOW); // Ensure motor is off initially

  // Start serial communication
  Serial.begin(9600);
  
  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();
}

void loop() {
  // Check for client connections
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Client connected!");
    String request = client.readStringUntil('\r');
    Serial.println("Request: " + request);
    client.flush();

    // If request contains "ON", activate the motor
    if (request.indexOf("ON") != -1) {
      digitalWrite(vibrationMotorPin, HIGH); // Turn on the motor
      Serial.println("Motor ON");
      delay(500); // Keep the motor on for 500ms
      digitalWrite(vibrationMotorPin, LOW); // Turn off the motor
      Serial.println("Motor OFF");
    }
    // Send response to client
    client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nMotor Activated");
    client.stop();
    Serial.println("Client disconnected.");
  }
}
