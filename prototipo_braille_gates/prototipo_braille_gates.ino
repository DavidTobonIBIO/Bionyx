#include <ESP32Servo.h>

Servo servo10min;
Servo servo3min;
Servo servoArrived;

// Servo[] servosArray = { servo10min, servo3min, servoArrived };

const int buttonPin = 14;
const int servoArrivedPin = 4; 
const int servo3minPin = 14; 
const int servo5minPin = 12;

int buttonState = HIGH;  
int lastButtonState = HIGH;

const int servoStartPos = 0;
const int servoActivePos = 90;

void setup() {
  servo10min.attach(servo5minPin);
  servo3min.attach(servo3minPin);
  servoArrived.attach(servoArrivedPin);
  
  servo10min.write(servoStartPos);
  servo3min.write(servoStartPos);
  servoArrived.write(servoStartPos);

  pinMode(buttonPin, INPUT);

  Serial.begin(115200);
}

void loop() {
  buttonState = digitalRead(buttonPin);
  Serial.println(buttonState);
  if (buttonState == HIGH && lastButtonState == LOW) {
    Serial.println("Button Pressed");
    // int randomServoIdx = random(0, 3);
    // Servo randomServo = servosArray[randomServoIdx];
    // randomServo.write(servoActivePos);

    Serial.println("Activating servo1");
    servo5min.write(servoActivePos);

    delay(10000);

    Serial.println("Deactivating servo1");
    servo5min.write(servoStartPos);

    Serial.println("Activating servo2");
    servo3min.write(servoActivePos);

    delay(2000);

    Serial.println("Deactivating servo2");
    servo3min.write(servoStartPos);

    Serial.println("Activating servo3");
    servoArrived.write(servoActivePos);

    delay(5000);
    
    Serial.prinln("Deactivating servo3");
    servoArrived.write(servoStartPos);

    lastButtonState = HIGH;
  } else {
    lastButtonState = buttonState;
  }
}
