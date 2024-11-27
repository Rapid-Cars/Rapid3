
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
  testESC();
  testSteering();
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

// Tests the function of the motor
void testESC() {
  setESCSpeed(0);
  setSteeringAngle(50);
  delay(1000);
  setESCSpeed(5);
  delay(1000);
  setESCSpeed(10);
  delay(1000);
  setESCSpeed(20);
  delay(1000);
  setESCSpeed(40);
  delay(1000);
  setESCSpeed(60);
  delay(1000);
  setESCSpeed(80);
  delay(1000);
  setESCSpeed(100);
  delay(1000);
  setESCSpeed(0);
  delay(1000);
}

// Tests the function of the steering
void testSteering() {
  setESCSpeed(0);
  setSteeringAngle(60);
  delay(1000);
  setSteeringAngle(70);
  delay(1000);
  setSteeringAngle(80);
  delay(1000);
  setSteeringAngle(90);
  delay(1000);
  setSteeringAngle(100);
  delay(1000);
  setSteeringAngle(40);
  delay(1000);
  setSteeringAngle(30);
  delay(1000);
  setSteeringAngle(20);
  delay(1000);
  setSteeringAngle(10);
  delay(1000);
  setSteeringAngle(0);
  delay(1000);
  setSteeringAngle(100);
  delay(1000);
  setSteeringAngle(50);
  delay (9000);
}

