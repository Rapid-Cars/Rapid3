
// The library Servo.h provides the functions for the motor and servo
#include "Servo.h"
#include <Wire.h>
#include <DFRobot_VL53L0X.h> // For the TOF sensor

//Constants for this project
//Motor / ESC
int escPin; // The pin where the ESC is attached to the Teensy
float escMaxSpeed; // Maximum speed of the motor (between 0.15 and 1)
float sensorMaxSpeed;
Servo esc;

//Servo
int servoPin; // The pin where the steering servo is attached
Servo steeringServo;

// Buffer for received Data
#define BUFFER_SIZE 32
char buffer[BUFFER_SIZE];

int speed = 0;   // Speed of the motor
int angle = 0;   // Steering angle of the servo
int count = 0;
int speeds[5];
int angles[5];

unsigned long lastReceiveTime = 0; // Tracks the last time data was received
const unsigned long timeout = 200; // 200 millisecond timeout

unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 100;

// Create an instance of the VL53L0X sensor
DFRobot_VL53L0X sensor;

void setup() {
  /*
  Pinout:
  P16: SCL1
  17: SDA1

  P19: SCL
  18: SDA
  */
  Serial.begin(115200);// Debug-Output
  Serial.println("Starting: \n");

  // Init esc
  escPin = 29;
  escMaxSpeed = 0.08;
  sensorMaxSpeed = 1;
  esc.attach(escPin, 1000, 2000);

  // Init servo
  servoPin = 28;
  steeringServo.attach(servoPin);

  // Init camera I2C
  Wire2.begin(0x12); // Teensy as Slave with adress 0x12
  Wire2.onReceive(receiveEvent); // Callback for received data

  // Init TOF I2C bus (for the VL53L0X sensor)
  Wire.begin();
  Wire.setClock(100000);
  sensor.begin(0x29); //Set I2C sub-device address
  sensor.setMode(sensor.eContinuous, sensor.eHigh);
  sensor.start();

  setESCSpeed(20);
  delay(100);
  setESCSpeed(0);
  delay(1000);
  setSteeringAngle(50);
}

void loop() {
  // Check for timeout
  if (millis() - lastReceiveTime > timeout) {
    Serial.println("Timeout: No data received for 200 milliseconds. Stopping car.");
    setESCSpeed(0); // Stop the car
    setSteeringAngle(50); // Set steering to neutral
    delay(2000);
    //exit(0); // Exit the program
  } else {
    // Process data from the camera
    if (millis() - lastSensorRead >= sensorInterval) {
      lastSensorRead = millis();
      processSensorData();
    }
    processCameraData(speed, angle);
    delay(10);
  }
  // For testing
  //driveTestCircle();
  //testESC();
  //testSteering();
  //exit(0);
}

// Dummy function to process data from the VL53L0X sensor
void processSensorData() {
  sensorMaxSpeed = 1;
  float distance = sensor.getDistance();
  if (distance<1 || distance > 2000) {
    return;
  }
  if (distance < 100) {
    sensorMaxSpeed = 0;
  }
}


// Processes the motor speed and steering angle.
// Uses the last five values for each to build an average value.
// The average value will then be sent to proper functions.
void processCameraData(int speed, int angle) {
  speeds[count] = speed;
  angles[count] = angle;
  count = count + 1;
  if (count > 4) {
    count = 0;
    int averageSpeed = 0;
    int averageAngle = 0;
    for (int i = 0; i < 5; i++) {
      averageSpeed += speeds[i];
      averageAngle += angles[i];
    }
    averageSpeed = averageSpeed / 5;
    averageAngle = averageAngle / 5;
    setESCSpeed(averageSpeed);
    setSteeringAngle(averageAngle);
  }
}

// Sets the speed of the esc
// int speed = value between 0 and 100
// The speed will get multiplied with the escMaxSpeed because the car won't need to go that fast.
void setESCSpeed(int speed) {
  speed = constrain(speed, 0, 100);
  if (speed == 0) {
    esc.write(0);
    return;
  }
  int maxSpeed = (int)(180 * escMaxSpeed * sensorMaxSpeed);
  speed = map(speed, 0, 100, 11, maxSpeed); // Scales the speed to use it with the servo (value between 0 and 180)
  speed = constrain(speed, 0, maxSpeed);
  esc.write(speed);
}

// int speed = value between 0 and 100
// 100 = full left, 50 = straight, 0 = full right
void setSteeringAngle(int angle) {
  angle = constrain(angle, 0, 100);
  angle = 100 - angle; // In Documentation 0 is full left and 100 is full right
  angle = map(angle, 0, 100, 50, 140); // Maps the values to the maximum angle the vehicle can achieve
  steeringServo.write(angle);
}

// Callback: receive data from Master (cam)
void receiveEvent(int numBytes) {
  int i = 0;
  while (Wire2.available() && i < BUFFER_SIZE - 1) {
    buffer[i++] = Wire2.read();
  }
  buffer[i] = '\0'; // Terminate string

  // Process CSV Input
  sscanf(buffer, "%d,%d", &speed, &angle);

  lastReceiveTime = millis();

  // Output received Data
  Serial.print("Empfangen - Speed: ");
  Serial.print(speed);
  Serial.print(", Steering angle: ");
  Serial.println(angle);
}

void driveTestCircle() {
  esc.write(0);
  setSteeringAngle(50);
  delay(5000);
  setESCSpeed(10);
  for (int i = 50; i<=100; i++) {
    setSteeringAngle(i);
    delay(20);
  }
  for (int i = 100; i>=50; i--) {
    setSteeringAngle(i);
    delay(20);
  }
}

// Tests the function of the motor
void testESC() {
  Serial.println("Testing ESC");
  setESCSpeed(0);
  Serial.println(0);
  //setSteeringAngle(50);
  setESCSpeed(20);
  Serial.println(20);
  delay(3000);
  setESCSpeed(40);
  Serial.println(40);
  delay(3000);
  setESCSpeed(60);
  Serial.println(60);
  delay(3000);
  setESCSpeed(80);
  Serial.println(80);
  delay(3000);
  setESCSpeed(100);
  Serial.println(100);
  delay(3000);
  setESCSpeed(0);
  Serial.println(0);
  delay(10000);
}

// Tests the function of the steering
void testSteering() {
  Serial.println("Testing steering");
  //setESCSpeed(0);
  setSteeringAngle(60);
  Serial.println(60);
  delay(1000);
  setSteeringAngle(70);
  Serial.println(70);
  delay(1000);
  setSteeringAngle(80);
  Serial.println(80);
  delay(1000);
  setSteeringAngle(90);
  Serial.println(90);
  delay(1000);
  setSteeringAngle(100);
  Serial.println(100);
  delay(1000);
  setSteeringAngle(40);
  Serial.println(40);
  delay(1000);
  setSteeringAngle(30);
  Serial.println(30);
  delay(1000);
  setSteeringAngle(20);
  Serial.println(20);
  delay(1000);
  setSteeringAngle(10);
  Serial.println(10);
  delay(1000);
  setSteeringAngle(0);
  Serial.println(0);
  delay(1000);
  setSteeringAngle(100);
  Serial.println(100);
  delay(1000);
  setSteeringAngle(0);
  Serial.println(0);
  delay(1000);
  setSteeringAngle(50);
  Serial.println(50);
  delay (9000);
}

