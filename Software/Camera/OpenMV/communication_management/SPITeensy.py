import time
# noinspection PyUnresolvedReferences
from machine import SPI, Pin

SPI_INSTANCE = None
CS = None

class SPITeensy:

    def __init__(self):
        self.setup_new_communication()


    def setup_new_communication(self):
        """
        Sets up the I2C communication. Resets the old one if called again
        """
        global SPI_INSTANCE, CS
        SPI_INSTANCE = SPI(1,  # the  bus which is chosen, openmv only has 1, so 0
                  baudrate=115200,  # 115.2kHz clock
                  polarity=0,  # CPOL = 0 (Clock idle low)
                  phase=0,  # CPHA = 0 (Data on rising edge)
                  # sck=Pin(2),              # SCK on GPIO2
                  # mosi=Pin(0),             # MOSI on GPIO0
                  # miso=Pin(1),             # MISO on GPIO1
                  # firstbit=SPI.MSB         # MSB-first transmission
                  )
        # Chip-select pin
        CS = Pin("P3", mode=Pin.OUT, value=1)  # CS starts inactive (HIGH)


    def send_movement_data(self, speed, steering):
        """
        Sends the speed and steering commands to the Teensy
        via I2C communication.
        """
        try:
            CS(0)  # Select the SPI slave (CS LOW)
            SPI_INSTANCE.write(bytes([speed]))  # Send speed (50)
            SPI_INSTANCE.write(bytes([steering]))  # Send steering (40)
        finally:
            CS(1)