#include <Arduino.h>
#include <algorithm> // For std::max and std::min
#include <Servo.h>
using namespace std;

uint32_t spiRx[10];
volatile int spiRxIdx;
volatile int spiRxComplete = 0;

#include "SPISlave_T4.h"
SPISlave_T4<&SPI, SPI_8_BITS> mySPI;



void processCameraData(int speed, int angle) {
  // Dummy function
}

void setup() {
  Serial.begin(115200);	//Baudrate does not matter (is USB VCP anyway)
  while ( ! Serial) {}
  Serial.println("START...");
  mySPI.begin();
  mySPI.swapPins(true);
}

void loop() {
  int i;
  int speed = 0;
  int steering = 0;
  if (spiRxComplete) {
    //Serial.println(spiRxIdx);
    for (i = 0; i < spiRxIdx; i++) {
      //Serial.print(spiRx[i]); Serial.print(" ");
      speed = spiRx[0];
      steering = spiRx[1];
    }
  Serial.print("speed: ");
  Serial.println(speed);
  Serial.print("steering: ");
  Serial.println(steering);
  processCameraData(speed, steering);
  spiRxComplete = 0;
  spiRxIdx = 0;
  //delay(1000);
  }
}
