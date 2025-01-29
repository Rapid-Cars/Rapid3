import time
# noinspection PyUnresolvedReferences
import sensor
# noinspection PyUnresolvedReferences
import machine
# noinspection PyUnresolvedReferences
import network
import socket
import os
# noinspection PyUnresolvedReferences
import mjpeg
# noinspection PyUnresolvedReferences
from libraries.lane_recognition import *
# noinspection PyUnresolvedReferences
from libraries.movement_params import *
# noinspection PyUnresolvedReferences
from machine import LED
# noinspection PyUnresolvedReferences
from machine import SPI, Pin


# region SPI configuration
spi = SPI(1,                        #the  bus which is chosen, openmv only has 1, so 0
          baudrate=115200,          # 115.2kHz clock
          polarity=0,               # CPOL = 0 (Clock idle low)
          phase=0,                  # CPHA = 0 (Data on rising edge)
          #sck=Pin(2),              # SCK on GPIO2
          #mosi=Pin(0),             # MOSI on GPIO0
          #miso=Pin(1),             # MISO on GPIO1
          #firstbit=SPI.MSB         # MSB-first transmission
          )
# Chip-select pin
cs = Pin("P3", mode=Pin.OUT, value=1)  # CS starts inactive (HIGH)

# endregion

# noinspection PyUnresolvedReferences
clock = time.clock()

speed = 0
steering = 50

while True:
    # Change values (dummy code)
    speed += 1
    steering += 2
    if speed > 100: speed = 0
    if steering > 100: steering = 0

    try:
        cs(0)                           # Select the SPI slave (CS LOW)
        spi.write(bytes([speed]))       # Send speed (50)
        spi.write(bytes([steering]))    # Send steering (40)
        print("Send speed: ", speed, " and steering: ", steering)
    finally:
        cs(1)