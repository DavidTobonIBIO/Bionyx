#include <Servo.h>

Servo servo5min;
Servo servo3min;
Servo servoArrived;

// Servo[] servosArray = { servo10min, servo3min, servoArrived };

const int servoArrivedPin = A2; 
const int servo3minPin = A1; 
const int servo5minPin = A0;

int buttonState = HIGH;  
int lastButtonState = HIGH;

const int servoStartPos = 0;
const int servoActivePos = 90;

void setup() {
  servo5min.attach(servo5minPin);
  servo3min.attach(servo3minPin);
  servoArrived.attach(servoArrivedPin);
  
  servo5min.write(servoStartPos);
  servo3min.write(servoStartPos);
  servoArrived.write(servoStartPos);


  Serial.begin(9600);

    delay(10000);

  Serial.println("Activating servo1");
  servo5min.write(servoActivePos);

  delay(10000);

  Serial.println("Deactivating servo1");
  servo5min.write(servoStartPos);

  Serial.println("Activating servo2");
  servo3min.write(servoActivePos);

  delay(5000);

  Serial.println("Deactivating servo2");
  servo3min.write(servoStartPos);

  Serial.println("Activating servo3");
  servoArrived.write(90);

  delay(5000);
    
  Serial.println("Deactivating servo3");
  servoArrived.write(servoStartPos);
}

void loop() {


}
