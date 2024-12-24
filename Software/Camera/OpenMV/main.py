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

# Initialize I2C
# Pinout:
# P4: SCL
# P5: SDA
i2c = machine.I2C(1, freq=100000)
SLAVE_ADDRESS = 0x12  # Address of Teensy

# noinspection PyUnresolvedReferences
clock = time.clock()

# Set up the lane_recognition and movement_params which should be used
# noinspection PyUnresolvedReferences
lane_recognition = get_lane_recognition_instance('BaseInitiatedLaneFinder')
# noinspection PyUnresolvedReferences
lane_recognition.setup(get_pixel_getter('camera'))
# noinspection PyUnresolvedReferences
movement_params = get_movement_params_instance('DominantLaneAngleDriver')

# Wi-Fi setup ----------------------------------------------------------------------
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
    data = wifi_client.recv(1024)
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

# End Wi-Fi Setup ------------------------------------------------------------------

# File saving ----------------------------------------------------------------------
CLIP_DURATION = 30              # Clip duration in seconds
CLIP_FOLDER = "/sdcard/clips"   # Folder for saving clips
FILENAME, VIDEO, START_TIME = None, None, None


def get_next_clip_index():
    """
    Determine the next available clip index for video clips stored in a specified
    folder. This function scans the folder to identify existing clip files in the
    format "clip_<index>.mjpeg" and determines the next sequential index to
    use, starting from 0 if no valid clip files are present.

    Returns
    -------
    int
        The next available clip index for a new file.
    """
    files = os.listdir(CLIP_FOLDER)
    clip_indices = [
        int(file.split("_")[1].split(".")[0])
        for file in files if file.startswith("clip_") and file.endswith(".mjpeg")
    ]
    return max(clip_indices, default=-1) + 1  # Start from 0 if no files exist


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
        FILENAME = "{}/clip_{:05d}.mjpeg".format(CLIP_FOLDER, CLIP_INDEX)
        CLIP_INDEX += 1
        VIDEO = mjpeg.Mjpeg(FILENAME)
        START_TIME = time.ticks_ms()
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


# End File saving ------------------------------------------------------------------

# Debug visuals --------------------------------------------------------------------
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

# End debug visuals ----------------------------------------------------------------

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
    sensor.skip_frames(time=2000)  # Time to stabilize the camera
    sensor.set_auto_gain(False)  # Disable automatic exposure
    sensor.set_auto_whitebal(False)  # Disable automatic white balance


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
    # Process video
    speed, steering = movement_params.get_movement_params(left_lane, right_lane)

    send_speed = int(speed)
    send_steering = int(steering)

    # Save video to sd card
    save_frame_to_file(img)

    # Draw the arrow representing speed and steering
    draw_arrow(img, speed, steering)

    # Send data via I2C to the Teensy ------------------------------------------
    try:
        # Format Data as CSV
        formatted_message = f"{send_speed},{send_steering}"
        i2c.writeto(SLAVE_ADDRESS, formatted_message.encode('utf-8'))  # Send
        print("Sent - Speed: ", send_speed, ", Steering: ", send_steering)
    except OSError as exception:
        pass
        #print("I2C Error:", e)

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


USE_WIFI = False # Change to True if you want to stream the video
server = None

setup_camera()
CLIP_INDEX = get_next_clip_index()
if USE_WIFI:
    setup_access_point()


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
        time.sleep_ms(100)
