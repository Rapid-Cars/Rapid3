#include <Wire.h>

// Buffer for received Data
#define BUFFER_SIZE 32
char buffer[BUFFER_SIZE];

int speed = 0;      // Speed of the motor
int steering = 0;   // Steering angle of the servo

void setup() {
  Wire.begin(0x12); // Teensy as Slave with adress 0x12
  Wire.onReceive(receiveEvent); // Callback for received data
  /*
  Pinout:
  P19: SCL
  18: SDA
  */
  Serial.begin(115200);         // Debug-Output
}

void loop() {
  // Here speed and steering will be processed
  processData(speed, steering);
  delay(100);
}

// Dummy processing function
void processData(int speed, int steering) {
  // Todo
}

// Callback: receive data from Master (cam)
void receiveEvent(int numBytes) {
  int i = 0;
  while (Wire.available() && i < BUFFER_SIZE - 1) {
    buffer[i++] = Wire.read();
  }
  buffer[i] = '\0'; // Terminate string

  // Process CSV Input
  sscanf(buffer, "%d,%d", &speed, &steering);
  // Output received Data
  Serial.print("Empfangen - Speed: ");
  Serial.print(speed);
  Serial.print(", Steering: ");
  Serial.println(steering);
}
