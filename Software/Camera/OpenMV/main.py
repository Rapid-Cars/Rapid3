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

# region Initialize I2C

# Pinout:
# P4: SCL
# P5: SDA
i2c = machine.I2C(1, freq=100000)
SLAVE_ADDRESS = 0x12  # Address of Teensy

# endregion

# noinspection PyUnresolvedReferences
clock = time.clock()

lane_recognition_name = 'CenterLaneFinder'
secondary_lane_recognition_name = 'None'
movement_params_name = 'CenterLaneDeviationDriver'
version = "0.3.0"

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

# region Wi-Fi setup

SSID = "OPENMV_AP"  # Network SSID
KEY = "1234567890"  # Network key (must be 10 chars)
HOST = ""
PORT = 8080
SOCKET = None

def setup_access_point():
    """
    Set up an access point with a given SSID, key, and channel, then activate it.

    This function configures and activates the WLAN interface in access point (AP)
    mode, applying the specified SSID, password key, and channel. After activation,
    it prints the SSID and the IP address of the access point to confirm that the
    AP mode was set up successfully.

    Returns:
        None
    """
    network.country('DE')
    wlan = network.WLAN(network.AP_IF)
    wlan.config(ssid=SSID, key=KEY, channel=2)
    wlan.active(True)
    print("AP mode started. SSID: {} IP: {}".format(SSID, wlan.ifconfig()[0]))


def stream_video(wifi_client):
    """
    Function to stream video data to a client via HTTP connection using a multipart/x-mixed-replace
    content type, suitable for streaming camera feeds.

    Parameters:
    client: Object used to handle client-specific operations. Must define methods such
             as 'recv' for receiving data and 'send' for sending HTTP responses.

    Raises:
    None
    """
    # Read request from client
    _ = wifi_client.recv(1024)
    # Should parse client request here

    # Send multipart header
    wifi_client.send(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    while True:
        main_loop(wifi_client)

# endregion

# region File saving

CLIP_DURATION = 15              # Clip duration in seconds
CLIP_FOLDER = "/sdcard/clips"   # Folder for saving clips
FILENAME, VIDEO, START_TIME = None, None, None
led = LED("LED_BLUE")

def get_next_clip_index():
    """
    Returns the index of the next video clip based on how many files there are in the directory
    """
    files = os.listdir(CLIP_FOLDER)
    return len(files)


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


base_name = generate_base_name(lane_recognition_name, secondary_lane_recognition_name, movement_params_name)
LED_STATE = True  # True for blue LED, False for green (off LED)


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
        FILENAME = "{}/{}_{:05d}.mjpeg".format(CLIP_FOLDER, base_name, CLIP_INDEX)
        CLIP_INDEX += 1
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

# region Debug visuals

def draw_arrow(canvas, vehicle_speed, steering_angle):
    """
    Draws an arrow on a canvas to represent vehicle speed and steering angle. The arrow's
    length corresponds to the vehicle's speed, while its direction is adjusted according
    to the steering angle. The arrow length is scaled proportionally to a defined maximum.

    Parameters:
        canvas: A drawing surface where the arrow will be drawn. It must have methods
                to retrieve width and height, and a method `draw_arrow` to render the
                arrow.
        vehicle_speed: A numeric value representing the vehicle's speed as a percentage
                       of maximum speed.
        steering_angle: A numeric value indicating the steering angle, where 0 is 45°
                        to the left, 50 is vertical, and 100 is 45° to the right.
    """
    img_width = canvas.width()
    img_height = canvas.height()

    base_x = img_width // 2  # Center of the image horizontally
    base_y = img_height - 10  # Bottom of the image

    # Calculate arrow length and direction
    max_length = 200  # Maximum arrow length
    arrow_length = int((vehicle_speed / 100) * max_length)

    # Steering angle (0 = 45° left, 50 = vertical, 100 = 45° right)
    angle_offset = (steering_angle - 50) * 0.45  # Map to degrees
    angle_radians = angle_offset * (3.14159 / 180)  # Convert to radians

    # Calculate arrow tip coordinates
    tip_x = int(base_x + arrow_length * -angle_radians)  # Horizontal deviation
    tip_y = int(base_y - arrow_length)  # Vertical length

    # Draw the arrow on the image
    canvas.draw_arrow(base_x, base_y, tip_x, tip_y, color=100, thickness=4)

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
    sensor.set_auto_gain(True)  # Disable automatic exposure
    sensor.set_auto_whitebal(True)  # Disable automatic white balance
    sensor.set_auto_exposure(False, exposure_us=15000)  # Set exposure to 15000 µs (adjust as needed)
    sensor.skip_frames(time=2000)  # Time to stabilize the camera

USE_WIFI = False # Change to True if you want to stream the video
server = None

setup_camera()
CLIP_INDEX = get_next_clip_index()
if USE_WIFI:
    setup_access_point()

# endregion

# region Main loop

LAST_LEFT_LANE = []
LAST_RIGHT_LANE = []
LAST_LEFT_COUNT = 0
LAST_RIGHT_COUNT = 0

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

def main_loop(_wifi_client = None):
    """
    Main loop for processing image frames and performing lane detection, controlling movement parameters,
    saving video, drawing directional arrows, communicating with external hardware via I2C, and optionally
    streaming video over Wi-Fi. This function integrates multiple components for autonomous driving
    functionality.

    Parameters:
        _wifi_client: Optional. A Wi-Fi client object used to stream video data over a
                      network if enabled. Defaults to None.

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

    """
    if not left_lane:
        global LAST_LEFT_LANE
        left_lane = LAST_LEFT_LANE
        global LAST_LEFT_COUNT
        LAST_LEFT_COUNT += 1
        if LAST_LEFT_COUNT > 3:
            LAST_LEFT_COUNT = 0
            LAST_LEFT_LANE = []
    else:
        LAST_LEFT_LANE = left_lane
        global LAST_LEFT_COUNT
        LAST_LEFT_COUNT = 0

    if not right_lane:
        global LAST_RIGHT_LANE
        right_lane = LAST_RIGHT_LANE
        global LAST_RIGHT_COUNT
        LAST_RIGHT_COUNT += 1
        if LAST_RIGHT_COUNT > 3:
            LAST_RIGHT_COUNT = 0
            LAST_RIGHT_LANE = []
    else:
        LAST_RIGHT_LANE = right_lane
        global LAST_RIGHT_COUNT
        LAST_RIGHT_COUNT = 0
    """
    # Process video
    speed, steering = movement_params.get_movement_params(left_lane, right_lane)

    send_speed = int(speed)
    send_steering = int(steering)

    # Save video to sd card
    save_frame_to_file(img)

    # Draw the arrow representing speed and steering
    # draw_arrow(img, speed, steering)

    # Send data via I2C to the Teensy ------------------------------------------
    try:
        # Format Data as CSV
        formatted_message = f"{send_speed},{send_steering}"
        i2c.writeto(SLAVE_ADDRESS, formatted_message.encode('utf-8'))  # Send
        print("Sent - Speed: ", send_speed, ", Steering: ", send_steering)
    except OSError as exception:
        pass
        print("I2C Error:", exception)

    # Stream video over Wi-Fi
    # Use 192.168.4.1:8080 to connect
    if USE_WIFI:
        cframe = img.to_jpeg(quality=35, copy=True)
        header = (
                "\r\n--openmv\r\n"
                "Content-Type: image/jpeg\r\n"
                "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )
        _wifi_client.sendall(header)
        _wifi_client.sendall(cframe)
    print(clock.fps())

# main loop
while True:
    if USE_WIFI:

        if server is None:
            # Create server socket
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            # Bind and listen
            server.bind([HOST, PORT])
            server.listen(5)
            # Set server socket to blocking
            server.setblocking(True)

        try:
            print("Waiting for connections..")
            client, addr = server.accept()
        except OSError as e:
            server.close()
            server = None
            print("server socket error:", e)
            continue

        try:
            # set client socket timeout to 2s
            client.settimeout(5.0)
            print("Connected to " + addr[0] + ":" + str(addr[1]))
            stream_video(client)
        except OSError as e:
            client.close()
            print("client socket error:", e)
            # sys.print_exception(e)
    else:
        main_loop()

# endregion
