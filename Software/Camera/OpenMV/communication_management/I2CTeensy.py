import time
# noinspection PyUnresolvedReferences
import machine

SLAVE_ADDRESS = 0x12
i2c = None

class I2CTeensy:

    def __init__(self):
        self.setup_new_communication()


    def setup_new_communication(self):
        """
        Sets up the I2C communication. Resets the old one if called again
        """

        # Pinout:
        # P4: SCL
        # P5: SDA
        global i2c

        if i2c is None:
            i2c = machine.I2C(1, freq=50000)
            return

        # Reset the i2c instance
        try:
            i2c = None
            time.sleep_ms(500)
            i2c = machine.I2C(1, freq=50000)
            print("Reset I2C bus")
        except Exception as exception:
            with open("/sdcard/i2c_log.txt", "a") as log:
                log.write("Failed to reset I2C bus: " + str(exception) + "\n")


    def send_movement_data(self, speed, steering):
        """
        Sends the speed and steering commands to the Teensy
        via I2C communication.
        """
        try:
            # Format Data as CSV
            formatted_message = f"{speed},{steering}"
            i2c.writeto(SLAVE_ADDRESS, formatted_message.encode("utf-8"))
        except OSError as exception:
            with open("/sdcard/i2c_log.txt", "a") as log:
                log.write("I2C Error: " + str(exception) + "\n")
            self.setup_new_communication()