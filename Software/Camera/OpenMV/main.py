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
from machine import LED

lane_recognition_name = 'CenterLaneFinder'
secondary_lane_recognition_name = 'None'
movement_params_name = 'CenterLaneDeviationDriver'
version = "0.3.0"


# region Initialize I2C

# Pinout:
# P4: SCL
# P5: SDA
i2c = machine.I2C(1, freq=100000)
SLAVE_ADDRESS = 0x12  # Address of Teensy

# endregion

# region Set up the lane_recognition and movement_params which should be used

# noinspection PyUnresolvedReferences
lane_recognition = get_lane_recognition_instance(lane_recognition_name)
# noinspection PyUnresolvedReferences
lane_recognition.setup(get_pixel_getter('camera'))

# noinspection PyUnresolvedReferences
secondary_lane_recognition = get_lane_recognition_instance(lane_recognition_name)
if secondary_lane_recognition:
    # noinspection PyUnresolvedReferences
    secondary_lane_recognition.setup(get_pixel_getter('camera'))

# noinspection PyUnresolvedReferences
movement_params = get_movement_params_instance(movement_params_name)

# endregion

# region File saving

CLIP_DURATION = 15              # Clip duration in seconds
BASE_CLIP_FOLDER = "/sdcard/clips"   # Folder for saving clips
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
    CURRENT_CLIP_FOLDER = "{}/{}_{:03d}".format(BASE_CLIP_FOLDER, BASE_NAME, FOLDER_INDEX)
    os.mkdir(CURRENT_CLIP_FOLDER)
    print("Created new clip folder: {}".format(CURRENT_CLIP_FOLDER))


def generate_base_name(lane_algorithm_name, secondary_lane_algorithm_name, movement_algorithm_name):
    """
            Generates a standardized base name for the video file based on the version
            and the selected algorithms for lane recognition and movement parameters.

            Parameters:
            - lane_algorithm_name: str
                Name of the primary lane recognition algorithm.
            - secondary_lane_algorithm_name: str
                Name of the secondary lane recognition algorithm.
            - movement_algorithm_name: str
                Name of the movement parameter algorithm.

            Returns:
            - str: A formatted base name string in the form:
                "CLIP-v{version}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"

            Raises:
            - ValueError: If any provided algorithm name is invalid.
    """
    # noinspection PyUnresolvedReferences
    lane_recognition_id = get_lane_recognition_id(lane_algorithm_name)
    # noinspection PyUnresolvedReferences
    secondary_lane_recognition_id = get_lane_recognition_id(secondary_lane_algorithm_name)
    # noinspection PyUnresolvedReferences
    movement_algorithm_id = get_movement_params_id(movement_algorithm_name)

    if lane_recognition_id == -1 or movement_algorithm_id == -1:
        raise ValueError("Invalid algorithm name provided.")

    # Generate the base name
    return f"CLIP-v{version}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"


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
        VIDEO.add_frame(frame) # Stream frame to file
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
    - Disables automatic gain and white balance to maintain consistent
      image settings.

    Returns:
        None
    """
    # Camera initialization
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)  # Grayscale mode
    sensor.set_framesize(sensor.QVGA)  # 320x240 pixels
    sensor.set_contrast(3)
    sensor.set_auto_gain(False)  # Disable automatic exposure
    # sensor.set_auto_exposure(False, exposure_us=15000)  # Set exposure to 15000 µs (adjust as needed)
    sensor.skip_frames(time=2000)  # Time to stabilize the camera

# noinspection PyUnresolvedReferences
clock = time.clock()

BASE_NAME = generate_base_name(lane_recognition_name, secondary_lane_recognition_name, movement_params_name)
create_new_clip_folder()

setup_camera()

# endregion

# region Main loop

def update_lane_data(lane, sec_lane):
    """
    Compares the y-values in lane and sec_lane, if there is the same y-value in both Lists
    If both lanes have the same y-value it calculates the average of both x-values.
    If only one lane has a specific y-value it uses the corresponding x-value.
    Afterward it returns the sorted and updated lane data.

    Parameters:
        lane (tuple): The lane of the first algorithm
        sec_lane (tuple): The second lane
    """
    # A dictionary from left lane with y being the Key-value und and x the to the Key-value belonging value.
    lane_dict = {y: x for y, x in lane}

    for y, x in sec_lane:
        if y in lane_dict:
            # Calculates the average if there is the same y-value in both lists and adds it to the dictionary
            lane_dict[y] = (lane_dict[y] + x) // 2
        else:
            # Adds a new element to the dictionary if there is a y-value ONLY existing in sec_lane
            lane_dict[y] = x

    # converts the dictionary into a list.
    updated_lane = sorted(lane_dict.items())
    return updated_lane

def reset_i2c_bus():
    global i2c
    try:
        i2c.deinit() # Deactivate I2C
        i2c = machine.I2C(1, freq=100000)
        print("Reset I2C bus")
    except Exception as e:
        print("Failed to reset I2C bus:", e)



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

    left_lane, right_lane = lane_recognition.recognize_lanes(img)

    if secondary_lane_recognition:
        # Use the secondary algorithm only if the main algorithm doesn't recognize enough Elements
        if len(left_lane) + len(right_lane) < 7:
            sec_left_lane, sec_right_lane = secondary_lane_recognition.recognize_lanes(img)
            left_lane = update_lane_data(left_lane, sec_left_lane)
            right_lane = update_lane_data(right_lane, sec_right_lane)

    # Process video
    speed, steering = movement_params.get_movement_params(left_lane, right_lane)

    send_speed = int(speed)
    send_steering = int(steering)

    # Save video to sd card
    save_frame_to_file(img)

    # Send data via I2C to the Teensy ------------------------------------------
    try:
        # Format Data as CSV
        formatted_message = f"{send_speed},{send_steering}"
        i2c.writeto(SLAVE_ADDRESS, formatted_message.encode('utf-8'))  # Send
        print("Sent - Speed: ", send_speed, ", Steering: ", send_steering)
    except OSError as exception:
        with open("/sdcard/i2c_log.txt", "a") as f:
            f.write("I2C Error: " + str(exception) + "\n")
        reset_i2c_bus()
        print("I2C Error:", exception)

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