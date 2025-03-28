import time
# noinspection PyUnresolvedReferences
import sensor
# noinspection PyUnresolvedReferences
import machine
import os
# noinspection PyUnresolvedReferences
import mjpeg
# noinspection PyUnresolvedReferences
from libraries.lane_recognition import *
# noinspection PyUnresolvedReferences
from libraries.movement_params import *
# noinspection PyUnresolvedReferences
from libraries.communication_management import *
# noinspection PyUnresolvedReferences
from machine import LED
from common import *

# region Initialize Communication Handler

# noinspection PyUnresolvedReferences
COMMUNICATION_MANAGER = get_communication_manager("DirectPWM")

# endregion

# region Set up the lane_recognition and movement_params which should be used

def set_mode():
    """
    Sets the desired driving mode.
    To set the mode you have to bridge Pin 1 with a pin between Pin 2 and Pin 6.
    In total, you can have 6 different modes (Mode 0: No connection)
    """
    out_pin = machine.Pin("P1", machine.Pin.OUT)
    out_pin.high()
    for i in range(2, 7):
        pin = machine.Pin("P" + str(i), machine.Pin.IN, machine.Pin.PULL_DOWN)
        if pin.value() == 1:
            out_pin.low()
            return i-1
    out_pin.low()
    return 0

# noinspection PyUnresolvedReferences
pixel_getter = get_pixel_getter('camera')
# noinspection PyUnresolvedReferences
lane_recognition, secondary_lane_recognition = setup_lane_recognition(pixel_getter, get_lane_recognition_instance)
# noinspection PyUnresolvedReferences
movement_params = setup_movement_params(get_movement_params_instance, set_mode())

# endregion

# region File saving

CLIP_DURATION = 10 # Clip duration in seconds
BASE_CLIP_FOLDER = "/sdcard/clips" # Folder for saving clips
CURRENT_CLIP_FOLDER, FILENAME = None, None
VIDEO, START_TIME = None, None
led = LED("LED_BLUE")
LED_STATE = True  # True for blue LED, False for green (off LED)
CLIP_INDEX = 0
FOLDER_INDEX = 0

def create_new_clip_folder():
    files = os.listdir(BASE_CLIP_FOLDER)
    global FOLDER_INDEX
    FOLDER_INDEX = len(files)

    global CURRENT_CLIP_FOLDER, BASE_NAME
    while True:
        try:
            CURRENT_CLIP_FOLDER = "{}/CLIP-{}_{:03d}".format(BASE_CLIP_FOLDER, BASE_NAME, FOLDER_INDEX)
            os.mkdir(CURRENT_CLIP_FOLDER)
            break
        except OSError:
            FOLDER_INDEX += 1
            pass
    print("Created new clip folder: {}".format(CURRENT_CLIP_FOLDER))


def save_frame_to_file(frame):
    """
    Saves a single frame to a file and manages video clipping. Starts a new clip if
    not already initiated, and saves frames to the active video. Closes the clip
    and starts a new one when the clip duration exceeds the defined limit.

    Args:
        frame: The frame to be saved into the current video clip if a clip is
               already being saved. The data type is determined by the specific
               implementation or external library in use.

    Raises:
        Exception: An exception is raised if saving the clip or adding the frame
                   fails due to any unforeseen issue.
    """
    global FILENAME, VIDEO, START_TIME
    if FILENAME is None:
        global CLIP_INDEX
        FILENAME = "{}/clip{:03d}.mjpeg".format(CURRENT_CLIP_FOLDER, CLIP_INDEX)
        VIDEO = mjpeg.Mjpeg(FILENAME)
        START_TIME = time.ticks_ms()
        global LED_STATE
        # Alternate LED colors between blue and green
        if LED_STATE:  # If True, turn the LED blue
            led.on()  # Turn on blue LED
            LED("LED_GREEN").off()  # Ensure green is off
        else:  # If False, turn the LED green
            LED("LED_BLUE").off()  # Ensure blue is off
            LED("LED_GREEN").on()  # Turn on green LED

        LED_STATE = not LED_STATE  # Toggle state for next clip
        CLIP_INDEX = CLIP_INDEX + 1
        print("Saving clip to:", FILENAME)

    try:
        VIDEO.add_frame(frame)  # Stream frame to file
        if time.ticks_diff(time.ticks_ms(), START_TIME) > CLIP_DURATION * 1000:
            VIDEO.close()
            print("Clip saved successfully.")
            global FILENAME
            FILENAME = None
    except Exception as exception:
        print("Failed to save clip:", exception)


# endregion

# region Setup

def setup_camera():
    """
    Initializes the camera with predetermined settings suitable for
    grayscale image capture. This setup is intended to ensure
    consistent image quality by disabling auto-adjustments and fixing
    the pixel format and frame size.

    The function performs the following steps:
    - Resets the camera to initial state
    - Sets the pixel format to grayscale
    - Sets the frame size to QVGA (320x240 pixels)
    - Skips frames for a specified time to allow the camera to stabilize
    - Disables automatic gain to maintain consistent image settings.

    Returns:
        None
    """
    # Camera initialization
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)  # Grayscale mode
    sensor.set_framesize(sensor.QQVGA)  # 320x240 pixels = QVGA, 160x120 pixels = QQVGA
    # sensor.set_contrast(3)
    # sensor.set_auto_gain(True)  # Disable automatic exposure
    # sensor.set_auto_exposure(False, exposure_us=15000)  # Set exposure to 15000 µs (adjust as needed)
    sensor.skip_frames(time=500)  # Time to stabilize the camera

# noinspection PyUnresolvedReferences
clock = time.clock()

# noinspection PyUnresolvedReferences
BASE_NAME = generate_base_name(get_lane_recognition_id, get_movement_params_id)
create_new_clip_folder()

setup_camera()

# endregion

# region Main loop

def main_loop():
    """
    Main loop for processing image frames and performing lane detection, controlling movement parameters,
    saving video, drawing directional arrows, communicating with external hardware via I2C, and optionally
    streaming video over Wi-Fi. This function integrates multiple components for autonomous driving
    functionality.

    Raises:
        OSError: Raised during I2C communication errors with the external hardware.
    """
    clock.tick()
    img = sensor.snapshot()  # Capture an image

    speed, steering = set_speed_and_steering(img, lane_recognition, secondary_lane_recognition, movement_params)

    # Save video to sd card
    save_frame_to_file(img)

    # Send data via I2C to the Teensy ------------------------------------------
    COMMUNICATION_MANAGER.send_movement_data(speed, steering)
    print("Sent speed and steering commands:", speed, steering)

    print(clock.fps())

# Watchdog Timer with 1 second timeout
wdt = machine.WDT(timeout=1000) # 1000 ms

# main loop
while True:
    try:
        wdt.feed()
        main_loop()
    except Exception as e:
        with open("/sdcard/log.txt", "a") as f:
            f.write("Main Loop Crash: " + str(e) + "\n")
        print("Main Loop Crash:", e)

# endregion