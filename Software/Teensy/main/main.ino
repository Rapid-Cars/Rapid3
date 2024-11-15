
// The library Servo.h provides the functions for the motor and servo
#include "Servo.h"

//Constants for this project
//Motor / ESC
int escPin; // The pin where the ESC is attached to the Teensy
float escMaxSpeed; // Maximum speed of the motor (between 0 and 1)
Servo esc;

//Servo
int servoPin; // The pin where the steering servo is attached
Servo steeringServo;


void setup() {
  // Init esc
  escPin = 1; //CHANGE BEFORE USE
  escMaxSpeed = 0.2;
  esc.attach(escPin, 1000, 2000);

  // Init servo
  servoPin = 1; //CHANGE BEFORE USE
  steeringServo.attach(servoPin);
}

void loop() {
  // put your main code here, to run repeatedly:
  //Auf Befehl warten (zB Poti, oder Schalter)
  setMotorSpeed(5);
  setSteeringAngle(10);
}

//Sets the speed of the motor
//float speed = value between 0 and 100
void setMotorSpeed(float speed) {
  float writeSpeed = speed * escMaxSpeed * 1;//Change 1 to Umrechnungsfaktor
  esc.write(writeSpeed);
}

void setSteeringAngle(int angle) {
  steeringServo.write(angle);
}


