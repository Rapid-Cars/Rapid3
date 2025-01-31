import machine
import time

# Initialize I2C
# Pinout:
# P4: SCL
# P5: SDA
i2c = machine.I2C(1, freq=100000)

slave_address = 0x12  # Adress of Teensy

# Sample values for speed and steering
speed = 0
steering = 50

while True:
    #img = sensor.snapshot()
    # Change values (dummy code)
    speed += 1
    steering += 2
    if speed > 100: speed = 0
    if steering > 100: steering = 0

    try:
        # Format Data as CSV
        message = f"{speed},{steering}"
        i2c.writeto(slave_address, message.encode('utf-8'))  # Send
        print("Gesendet - Speed: ", speed, ", Steering: ", steering)
    except OSError as e:
        print("I2C Fehler:", e)

    time.sleep_ms(100)  # Interval between cycles
