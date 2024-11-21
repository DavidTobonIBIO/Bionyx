const int buttonPin = 34;
int buttonState = 0;

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT);
}

void loop() {
  int buttonState = digitalRead(buttonPin);
  Serial.println(buttonState);
  delay(200);
}
