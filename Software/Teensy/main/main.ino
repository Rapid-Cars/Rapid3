
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

// Sets the speed of the esc
// int speed = value between 0 and 100
// The speed will get multiplied with the escMaxSpeed because the car won't need to go that fast.
void setESCSpeed(int speed) {
  speed = constrain(speed, 0, 100);
  speed = speed * escMaxSpeed;
  speed = map(speed, 0, 100, 0, 180); // Scales the speed to use it with the servo (value between 0 and 180)
  esc.write(speed);
}

// int speed = value between 0 and 100
// 0 = full left, 50 = straight, 100 = full right
void setSteeringAngle(int angle) {
  angle = constrain(angle, 0, 100);
  angle = map(angle, 0, 100, 0, 180); // Scales the angle to use it with the servo (value between 0 and 180)
  steeringServo.write(angle);
}


