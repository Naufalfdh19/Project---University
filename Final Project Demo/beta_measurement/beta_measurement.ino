
#include <Servo.h>

Servo upperArm;
Servo foreArm;

void setup() {

  upperArm.attach(6);
  foreArm.attach(9);
  foreArm.write(90); // ubah nilainya ke 180 apabila ingin mengukur sudut maksimum
  Serial.begin(9600);
  
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte from serial
    String receivedChar = Serial.readString();
    int angle = receivedChar.toInt();
    Serial.println(angle);
    upperArm.write(180-angle);
    Serial.print(angle);
  }
}
