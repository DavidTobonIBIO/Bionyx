#include <ESP8266WiFi.h>

// Wi-Fi credentials
const char* ssid = "ColdPalmer"; // Replace with your Wi-Fi SSID
const char* password = "david4567"; // Replace with your Wi-Fi password

// Pin for the vibration motor
const int vibrationMotorPin =16; // D1 on NodeMCU

void reconnectToWiFi();
void sendVibrations(int minutesToArrive);

// Wi-Fi server
WiFiServer server(80);

void setup() {
  // Set motor pin as output
  pinMode(vibrationMotorPin, OUTPUT);
  digitalWrite(vibrationMotorPin, LOW); // Ensure motor is off initially

  // Start serial communication
  Serial.begin(115200);
  
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
  if (WiFi.status() != WL_CONNECTED) {
    reconnectToWiFi();
  }

  // Check for client connections
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Client connected!");
    String request = client.readStringUntil('\r');
    Serial.println("Request: " + request);
    client.flush();

    // If request contains "ON", activate the motor
    if (request.indexOf("5MIN") != -1) {
      Serial.println("Bus arriving in 5 minutes");
      sendVibrations(5);
    } else if (request.indexOf("3MIN") != -1) {
      Serial.println("Bus arriving in 3 minutes");
      sendVibrations(3);
    } else if (request.indexOf("ARRIVED") != -1) {
      Serial.println("Bus arrived");
      sendVibrations(0);
    } else if (request.indexOf("DOOR") != -1) {
      Serial.println("Person is at the correct door");
      sendVibrations(-1);
    }
    // Send response to client
    // client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nMotor Activated");
    // client.stop();
    // Serial.println("Client disconnected.");
  }
}

void reconnectToWiFi() {
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void sendVibrations(int minutesToArrive) {
  switch(minutesToArrive) {
    case 5:
      for (int i = 0; i < 2; i++) {
        digitalWrite(vibrationMotorPin, HIGH); 
        delay(500); 
        digitalWrite(vibrationMotorPin, LOW);
        delay(500);
      }
      break;
    case 3:
      for (int i = 0; i < 3; i++) {
        digitalWrite(vibrationMotorPin, HIGH); 
        delay(500); 
        digitalWrite(vibrationMotorPin, LOW);
        delay(500);
      }
      break;
    case 0:
      digitalWrite(vibrationMotorPin, HIGH); 
      delay(3000); 
      digitalWrite(vibrationMotorPin, LOW);
      break;
    case -1:
      digitalWrite(vibrationMotorPin, HIGH); 
      delay(500); 
      digitalWrite(vibrationMotorPin, LOW);
      break;
    default:
      digitalWrite(vibrationMotorPin, LOW);
      break;
  }
}
