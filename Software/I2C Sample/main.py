import machine
import time

# Initialize I2C
# Pinout:
# P4: SCL
# P5: SDA
i2c = machine.I2C(1, freq=100000)

slave_address = 0x12  # Adress of Teensy

# Sample values for speed and steering
speed = 100
steering = 45

while True:
    # Change values (dummy code)
    speed += 1
    steering += 2
    if speed > 200: speed = 100
    if steering > 90: steering = -90

    try:
        # Format Data as CSV
        message = f"{speed},{steering}"
        i2c.writeto(slave_address, message.encode('utf-8'))  # Send
        print("Gesendet - Speed: ", speed, ", Steering: ", steering)
    except OSError as e:
        print("I2C Fehler:", e)

    time.sleep_ms(1)  # Interval between cycles
