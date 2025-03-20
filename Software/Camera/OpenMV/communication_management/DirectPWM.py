import time
# noinspection PyUnresolvedReferences
from machine import PWM, Timer

# region init values

# Motor-PWM
ESC_PIN = "P9"
ESC_FREQUENCY = 50

# Steering Servo
SERVO_PIN = "P7"
SERVO_FREQUENCY = 50

# Init PWM
esc_pwm = PWM(ESC_PIN, freq=ESC_FREQUENCY, duty_u16=0)
servo_pwm = PWM(SERVO_PIN, freq=SERVO_FREQUENCY, duty_u16=0)

# Max Servo speed (scaling factor)
ESC_MAX_SPEED = 0.16

# Values for the servos
esc_value = 0
steering_value = 0

# Timer for asynchronous updates
update_timer = Timer()

# endregion

class DirectPWM:

    def __init__(self):
        self.setup_new_communication()


    def setup_new_communication(self):
        """
        Sets up the motor-esc and sets the steering value to 50 (straight).
        Initializes a timer which updates the speed and steering 100 times per seconds.
        """
        print("Starting esc")
        # Start esc
        start_time = time.ticks_ms()
        while True:
            esc_pwm.duty_u16(3000)
            if (time.ticks_ms() - start_time) > 2500:
                break
        self.set_esc_speed(0)
        self.set_steering_value(50)

        update_timer.init(freq=100, mode=Timer.PERIODIC, callback=self.update_pwm)


    def update_pwm(self, t):
        """
        This function is called periodically by the timer to update the ESC and servo values
        """
        esc_pwm.duty_u16(esc_value)
        servo_pwm.duty_u16(steering_value)



    def send_movement_data(self, speed, steering):
        """
        Receives the movement data from the main algorithm and sets those values for the esc and servo.
        """
        # This function will be called from main.py when a new value is processed
        self.set_esc_speed(speed)
        self.set_steering_value(steering)

    def set_esc_speed(self, speed):
        """
        Updates the esc speed by translating the value to the corresponding PWM value.
        """
        global esc_value
        speed = max(0, min(speed, 100))
        if speed == 0:
            esc_value = 0
            return
        speed = speed * ESC_MAX_SPEED
        esc_value = int(self.map_value(speed, 3500, 4000))

    def set_steering_value(self, steering):
        """
        Updates the steering value by translating the value to the corresponding PWM value.
        """
        global steering_value
        steering = max(0, min(steering, 100))
        steering = 100 - steering

        if steering < 50:
            steering_value = int(self.map_value(steering, 3150, 4300, in_min=0, in_max=49))
        else:
            steering_value = int(self.map_value(steering, 4300, 6300, in_min=50, in_max = 100))

    def map_value(self, input_value, out_min, out_max, in_min=0, in_max=100):
        """
        Maps an input value in a given input range to an output range.
        """
        return out_min + ((input_value - in_min) / (in_max - in_min)) * (out_max - out_min)

# Testing area
"""
a = DirectPWM() # Just for debugging this class
while True:
    print("Testing speed")
    for speed in range(0, 100):
        a.send_movement_data(speed, 50)
        time.sleep_ms(100)

    print("Testing steering")
    for steering in range(0, 100):
        a.send_movement_data(0, steering)
        time.sleep_ms(10)

    for steering in range(100, 0, -1):
        a.send_movement_data(0, steering)
        time.sleep_ms(10)
"""
