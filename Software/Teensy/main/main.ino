#include <Wire.h>
#include <DFRobot_VL53L0X.h>

bool sensorTriggered = false;
unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 100;

const int triggerPin = 10;

bool lastTrigger = false;

//Create an instance of the VL53L0X sensor
DFRobot_VL53L0X sensor;

void setup() {
  Serial.begin(115200);
  Serial.println("Starting: \n");

  pinMode(triggerPin, OUTPUT);

  //init TOF bus (for the VL53L0X sensor)
  Wire.begin();
  Wire.setClock(100000);
  sensor.begin(0x29);
  sensor.setMode(sensor.eContinuous, sensor.eHigh);
  sensor.start();

}

void loop() {
  /*if (millis() - lastSensorRead >= sensorInterval) {
    lastSensorRead = millis();
    
  }*/
  processSensorData();
  if (sensorTriggered) {
    digitalWrite(triggerPin, HIGH);
  } else {
    digitalWrite(triggerPin, LOW);
  }
  if (lastTrigger != sensorTriggered) {
    if (sensorTriggered) {
      Serial.println("Stopping");
    } else {
      Serial.println("Starting");
    }
  }
  lastTrigger = sensorTriggered;
}

void processSensorData() {
  float distance = sensor.getDistance();
  //Serial.print("Distance: ");
  //Serial.println(distance);
  if (distance < 300) {
    sensorTriggered = true;
  } else {
    sensorTriggered = false;
  }
}