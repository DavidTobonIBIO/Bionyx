#include <WiFi.h> // Use WiFi.h for ESP32

// Wi-Fi credentials
const char* ssid = "ColdPalmer"; // Replace with your Wi-Fi SSID
const char* password = "david4567"; // Replace with your Wi-Fi password

const int buttonPin = 34;
int lastButtonState = LOW;
int buttonState = LOW;

// ESP32's target server IP and port
const char* serverIP = "192.168.125.169"; // Replace with the server's IP address
const int serverPort = 80;

void sendBusArrivalVibrations();
void reconnectToWiFi();
void personArrived();
void busArrivingIn5();
void busArrivingIn3();
void busArrived();

void setup() {
  // Start serial communication
  Serial.begin(115200);
  pinMode(buttonPin, INPUT);

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
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    reconnectToWiFi();
  }

  int buttonState = digitalRead(buttonPin);
  Serial.print("Button state is: ");
  Serial.println(buttonState);

  if (buttonState == HIGH && lastButtonState == LOW) {
    Serial.println("Person requested aid");
    personArrived();
    delay(10000); // Sim
    sendBusArrivalVibrations();
  }
  lastButtonState = buttonState;
  delay(1000);
}


void sendBusArrivalVibrations() {
  // Sim
  Serial.println("Bus arriving in 5");
  busArrivingIn5();
  delay(15000);
  Serial.println("Bus arriving in 3");
  busArrivingIn3();
  delay(10000);
  Serial.println("Bus arrived");
  busArrived();
}

void busArrivingIn5() {
    WiFiClient client;
    if (client.connect(serverIP, serverPort)) {
      // Send the request
      client.println("GET /5MIN HTTP/1.1");
      client.println("Host: " + String(serverIP));
      client.println("Connection: close");
      client.println();

      client.stop();
      Serial.println("Signal sent!");
    }

}

void busArrivingIn3() {
  WiFiClient client;
    if (client.connect(serverIP, serverPort)) {
      // Send the request
      client.println("GET /3MIN HTTP/1.1");
      client.println("Host: " + String(serverIP));
      client.println("Connection: close");
      client.println();

      client.stop();
      Serial.println("Signal sent!");
    }
}

void busArrived() {
    WiFiClient client;
    if (client.connect(serverIP, serverPort)) {
      // Send the request
      client.println("GET /ARRIVED HTTP/1.1");
      client.println("Host: " + String(serverIP));
      client.println("Connection: close");
      client.println();

      client.stop();
      Serial.println("Signal sent!");
    }
}

void personArrived() {
  WiFiClient client;
    if (client.connect(serverIP, serverPort)) {
      // Send the request
      client.println("GET /DOOR HTTP/1.1");
      client.println("Host: " + String(serverIP));
      client.println("Connection: close");
      client.println();

      client.stop();
      Serial.println("Signal sent!");
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
