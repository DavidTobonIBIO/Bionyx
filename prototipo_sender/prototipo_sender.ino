#include <WiFi.h> // Use WiFi.h for ESP32

// Wi-Fi credentials
const char* ssid = "ColdPalmer"; // Replace with your Wi-Fi SSID
const char* password = "david4567"; // Replace with your Wi-Fi password

// ESP32's target server IP and port
const char* serverIP = "192.168.125.169"; // Replace with the server's IP address
const int serverPort = 80;

void setup() {
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
}

void loop() {
  // Simulate sending signal to the server
  Serial.println("Sending signal to activate motor...");
  
  // Connect to the server
  WiFiClient client;
  if (client.connect(serverIP, serverPort)) {
    // Send the request
    client.println("GET /ON HTTP/1.1");
    client.println("Host: " + String(serverIP));
    client.println("Connection: close");
    client.println();

    // Read the response
    while (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
    }

    client.stop();
    Serial.println("Signal sent!");
  } else {
    Serial.println("Failed to connect to server.");
  }

  delay(5000); // Wait for 5 seconds before sending the next signal
}
