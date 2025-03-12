import platform
import re
import subprocess
import cv2
import os
import json
import gzip
from tkinter import Tk, filedialog

from Software.Camera.lane_recognition import *
from Software.Camera.movement_params import *
from common import *

HEIGHT = 240
WIDTH = 320

# region Debug visualisations -------------------------------------------------------------

def draw_debug_visuals(img, primary, left_lane, main_lane_recognition, process_left_lane, process_right_lane, right_lane,
                       sec_left_lane, sec_right_lane, secondary_lane_recognition, speed, steering):
    """
        Draws debug visuals on an image to aid in lane detection analysis.

        Parameters:
            img (numpy.ndarray): The image to draw on.
            primary (bool): Indicates if primary detection mode is active.
            left_lane (list): Coordinates of the left lane markings.
            main_lane_recognition (lane recognition or bool): Data for the main lane recognition area (details TBD).
            process_left_lane (list): Coordinates of intermediate processed left lane markings.
            process_right_lane (list): Coordinates of intermediate processed right lane markings.
            right_lane (list): Coordinates of the right lane markings.
            sec_left_lane (list): Coordinates of secondary left lane markings.
            sec_right_lane (list): Coordinates of secondary right lane markings.
            secondary_lane_recognition (lane recognition or bool): Whether to display secondary lane recognition visuals.
            speed (float): Current speed of the car.
            steering (float): Current steering angle of the car.
    """

    # Set colors
    if primary:
        left_lane_color = (0, 0, 255)
        right_lane_color = (0, 255, 0)
        sec_left_lane_color = (255, 0, 0)
        sec_right_lane_color = (0, 165, 255)
        process_left_lane_color = (255, 0, 255)
        process_right_lane_color = (255, 255, 0)
        line_thickness = 2
    else:
        left_lane_color = (128, 128, 255)
        right_lane_color = (128, 255, 128)
        sec_left_lane_color = (255, 128, 128)
        sec_right_lane_color = (128, 200, 255)
        process_left_lane_color = (192, 128, 192)
        process_right_lane_color = (255, 255, 128)
        line_thickness = 1


    # Draws the searchable area of the algorithm
    if primary:
        draw_search_area(img, main_lane_recognition)  # NOT Implemented yet
    # Draws the ignore zone (zone where the car is visible
    draw_ignore_zone(img)
    # Draws the found lane markings
    draw_lanes(img, left_lane, right_lane, 5, left_lane_color, right_lane_color, line_thickness)
    if secondary_lane_recognition:
        draw_lanes(img, sec_left_lane, sec_right_lane, 5, sec_left_lane_color, sec_right_lane_color, line_thickness)
    draw_lanes(img, process_left_lane, process_right_lane, 2, process_left_lane_color, process_right_lane_color, -1)
    # Draws the speed and steering value of the car
    draw_speed(img, speed, primary)
    draw_steering(img, steering, primary)


def draw_lanes(img, left_lane, right_lane, radius, left_lane_color, right_lane_color, line_thickness):
    """
        Draws lane markings on the given image.

        Parameters:
        - img: ndarray
            The image on which to draw the lanes.
        - left_lane, right_lane: list
            Lists of lane points to be drawn.
        - radius: int
            Radius of the circles that will be drawn.
        - left_lane_color, right_lane_color: tuple
            Colors for the left and right lane points, respectively.
        - line_thickness: int
            Thickness of the lane markings.
    """
    draw_lane(img, left_lane, radius, left_lane_color, line_thickness)
    draw_lane(img, right_lane, radius, right_lane_color, line_thickness)


def draw_lane(img, lane, radius, color, line_thickness):
    """
        Helper function to draw individual lane points on the image.

        Parameters:
        - img: ndarray
            The image on which to draw the lane.
        - lane: list
            A list of lane points (tuples of coordinates).
        - radius: int
            Radius of the points.
        - color: tuple
            Color of the points.
        - line_thickness: int
            Thickness of the points.
    """
    if lane:
        for element in lane:
            if element is not None:
                cv2.circle(img, (element[1], element[0]), radius, color, line_thickness)


def get_ignore_zone():
    """
        Determines the ignore zone of the given image.
        The ignore zone is a zone in the image where the car is visible and where the lane recognition
        is therefore unreliable.

        Returns:
        - tuple: (x_min, y_min, x_max, y_max) specifying the ignore zone's rectangle.
    """
    y_min = HEIGHT
    y_max = 115
    x_min = 110
    x_max = 240
    return x_min, y_min, x_max, y_max


def draw_ignore_zone(img):
    """
        Draws a rectangle on the image to represent the ignore zone.

        Parameters:
        - img: ndarray
            The image on which to draw the ignore zone.
    """
    x_min, y_min, x_max, y_max = get_ignore_zone()
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max + 1), (0, 0, 0), 2)


def draw_search_area(img, lane_recognition):
    """
        Placeholder function for drawing the search area on the image.

        Parameters:
        - img: ndarray
            The image on which to draw the search area.
        - lane_recognition: object
            Lane recognition instance containing the search area information.
    """
    pass
    """
    ToDo: Implement a function lane_recognition.get_search_area
    This function should return a list
    - ignore_zone: bool (ignore zone is specified here so it should return whether it uses the ignore zone)
    - outside border: A list with rectangles that specify the outside border
    - scan lines: A list with rectangles that are NOT the scan lines
    
    With this information every part of the image that is not processed will be a certain color
    This makes debugging easier because you can understand what the camera sees
    """


def draw_speed(img, vehicle_speed, primary):
    """
    Draws a vertical red line on the given image to represent speed.
    The line is drawn on the left side of the image and its length is
    proportional to the given speed (0 to 100).

    Parameters:
    - img: ndarray (color image)
    - speed: int (0-100)
    """
    line_base_y = HEIGHT - 20
    max_line_length = (HEIGHT - 40)
    max_line_end_y = line_base_y - max_line_length
    if primary:
        x_position = 10
        color = (0, 0, 255)
    else:
        x_position = 20
        color = (127, 127, 255)
    # Draws background line to indicate the full speed range
    cv2.line(img, (x_position, line_base_y), (x_position, max_line_end_y), (50, 50, 50), 3)

    # Draws the line to represent the calculated speed
    line_length = int(max_line_length * (vehicle_speed / 100))
    line_end_y = line_base_y - line_length
    cv2.line(img, (x_position, line_base_y), (x_position, line_end_y), color, 1)


def draw_steering(img, steering_angle, primary):
    """
    Draws a horizontal red line on the given image to represent steering angle.
    The line is drawn on the bottom of the image with the start position in the horizontal middle.
    Its direction and length is proportional to the given steering angle.

    Parameters:
    - img: ndarray (color image)
    - steering_angle: int (0-100, 50=neutral)
    """
    if steering_angle < 0:
        steering_angle = 0
    if steering_angle > 100:
        steering_angle = 50

    line_base_x = 20
    max_line_length = (WIDTH - 40) // 2
    max_line_end_x = line_base_x + max_line_length * 2

    if primary:
        y_position = HEIGHT - 10
        color = (0, 0, 255)
    else:
        y_position = HEIGHT - 20
        color = (127, 127, 255)

    # Draws background line to indicate the full steering range
    cv2.line(img, (line_base_x, y_position), (max_line_end_x, y_position), (50, 50, 50), 3)

    line_start_x = WIDTH // 2
    line_length = int(max_line_length * (steering_angle - 50) / 100)
    line_length = line_length * 2
    line_end_x = line_start_x + line_length
    cv2.line(img, (line_start_x, y_position), (line_end_x, y_position), color, 1)

# endregion

# region File name handling ---------------------------------------------------------------

def set_input_and_output(input_path, video_name, processing_name):
    """
        Prepares the input and output file paths for video processing.

        Parameters:
        - input_path: str
            The directory where the input video file is located.
        - video_name: str
            The name of the input video file, including its extension (e.g., "video.mp4").
        - processing_name: str
            A descriptive name or label for the processing pipeline typically generated with generate_base_name().

        Returns:
        - tuple: (input_video, output_video)
            - input_video: str
                Full path to the input video file.
            - output_video: str
                Full path for saving the processed output video, formatted as:
                "{input_path}/Processed/{video_name_without_extension} - Processed with {processing_name}.avi".

        Prints:
        - The paths of the input and output video files for confirmation.
    """
    if not os.path.exists(input_path):
        raise ValueError(f"Input path does not exist: {input_path}")
    output_directory = os.path.join(input_path, "Processed")
    if not os.path.exists(output_directory):
        print("Output directory does not exist. Creating it.")
        os.makedirs(output_directory)

    input_video = os.path.join(input_path, video_name)

    if not os.path.exists(input_video):
        raise ValueError(f"Input video file {input_video} does not exist.")

    print("Processing: ", input_video)

    # Remove the extension from video_name
    base_name = os.path.splitext(video_name)[0]
    output_video = os.path.join(output_directory, f"{base_name} - Processed with {processing_name}.avi")

    print("Saving output to: ", output_video)
    return input_video, output_video

# endregion

# region json analysis --------------------------------------------------------------------

JSON_INPUT_PATH = ""
JSON_OUTPUT_PATH = ""

def set_json_path(input_path, output_path):
    """
    Sets JSON file paths.
    """
    global JSON_INPUT_PATH
    global JSON_OUTPUT_PATH
    if input_path:
        if os.path.exists(input_path):
            JSON_INPUT_PATH = input_path
    JSON_OUTPUT_PATH = output_path


def convert_values_to_json(frame, left_lane, right_lane, sec_left_lane, sec_right_lane, speed, steering):
    """
    Converts the values of the given frame to JSON.
    """
    data = {
            "f": frame,
            "ll": left_lane,
            "rl": right_lane,
            "sll": sec_left_lane,
            "srl": sec_right_lane,
            "spd": speed,
            "str": steering
        }
    return data


def save_analysis_to_file(all_frame_data):
    """
    Save all analyzed data to a compressed JSON file in one operation.

    Parameters:
        all_frame_data (list of dict): List of dictionaries containing data for all frames.
    """
    try:
        # Use the given data directly and save it in one go
        with gzip.open(JSON_OUTPUT_PATH, 'wt') as f:
            json.dump(all_frame_data, f, separators=(',', ':'))  # Compact format

        print(f"All frame data successfully saved to {JSON_OUTPUT_PATH}")
    except Exception as e:
        print(f"Failed to save all frame data: {e}")


def load_analysis_from_file():
    """
    Load analyzed data from a JSON file.

    Returns:
        list of dict: List of dictionaries containing frame data.
    """
    try:
        with gzip.open(JSON_INPUT_PATH, 'rt') as f:
            data = json.load(f)
        print(f"JSON-Data successfully loaded from {JSON_INPUT_PATH}")
        return data
    except Exception as e:
        print(f"Failed to load json data: {e}")
        return None


def get_frame_data(frame, data: json):
    """
    Retrieve data for a specific frame from the JSON file.

    Parameters:
        frame (int): The frame number to retrieve data for.
        data (json): The json data

    Returns:
        tuple: left_lane, right_lane, sec_left_lane, sec_right_lane, speed, steering
    """
    try:
        if data is None:
            return None

        for frame_data in data:
            if frame_data.get("f") == frame:
                # Convert back to full keys for compatibility
                return (
                    frame_data.get("ll"),
                    frame_data.get("rl"),
                    frame_data.get("sll"),
                    frame_data.get("srl"),
                    frame_data.get("spd"),
                    frame_data.get("str"),
                )
        print(f"Frame {frame} not found in the data.")
        return None
    except Exception as e:
        print(f"Failed to retrieve frame data: {e}")
        return None

# endregion

# region Video processing -----------------------------------------------------------------

def load_video(main_lane_recognition, secondary_lane_recognition, movement_params, input_video, output_video):
    """
    Load and process a video using OpenCV.

    This function initializes the video capture and writer objects, reads
    frames from an input video, processes each frame, and writes the
    processed frames to an output video file. It also displays each frame
    in a window until the video ends or the user closes the window.
    """

    cap = cv2.VideoCapture(input_video)
    # noinspection PyUnresolvedReferences
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video, fourcc, 30.0, (320, 240))

    frame_count = 1
    json_compare_data = load_analysis_from_file()
    output_data = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        json_compare_frame_data = get_frame_data(frame_count, json_compare_data)
        json_data = process_frame(frame, main_lane_recognition, secondary_lane_recognition, movement_params, json_compare_frame_data, frame_count)
        output_data.append(json_data)
        out.write(frame)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_count += 1

    save_analysis_to_file(output_data)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def process_frame(img, main_lane_recognition, secondary_lane_recognition, movement_params, json_compare_frame_data, frame_count):
    """
    Process a single video frame to recognize and highlight lane lines, and
    calculate movement parameters such as speed and steering angle.

    Parameters:
    img : np.ndarray
        The image frame to be processed, expected in BGR format.
    lane_recognizer : LaneRecognizer
        An instance of LaneRecognizer used to identify lane lines in the image.

    Global Variables:
    HEIGHT : int
        The height of the image frame, derived from the shape of img.
    WIDTH : int
        The width of the image frame, derived from the shape of img.

    The function processes a video frame by converting it to grayscale and
    using a lane recognition module to identify the left and right lane lines.
    It calculates movement parameters, including speed and steering angles,
    based on the recognized lanes. Additionally, it draws debug visualizations
    """
    global HEIGHT, WIDTH
    HEIGHT, WIDTH = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Video processing

    speed, steering, left_lane, right_lane, sec_left_lane, sec_right_lane, process_left_lane, process_right_lane \
        = set_speed_and_steering(gray, main_lane_recognition, secondary_lane_recognition, movement_params, return_lanes=True)

    draw_debug_visuals(img, True, left_lane, main_lane_recognition, process_left_lane, process_right_lane, right_lane,
                       sec_left_lane, sec_right_lane, secondary_lane_recognition, speed, steering)

    # region json handling
    # Saves the current values to a json file
    json_data = convert_values_to_json(frame_count,
                                       left_lane, right_lane,
                                       sec_left_lane, sec_right_lane,
                                       speed, steering)

    # Draws the data of the given json file (json_compare_frame_data) on the screen

    if not json_compare_frame_data:
        return json_data

    (json_left_lane, json_right_lane,
     json_sec_left_lane, json_sec_right_lane,
     json_speed, json_steering) = json_compare_frame_data

    if json_left_lane and json_right_lane:
        json_has_secondary = True
    else:
        json_has_secondary = False

    json_process_left_lane = left_lane
    json_process_right_lane = right_lane

    if json_has_secondary:
        # Use secondary algorithm if a lane is empty
        if not json_left_lane or not json_right_lane:
            if len(json_sec_left_lane) > len(json_left_lane):
                json_process_left_lane = json_sec_left_lane
            if len(json_sec_right_lane) > len(json_right_lane):
                json_process_right_lane = json_sec_right_lane

    draw_debug_visuals(img, False, json_left_lane, None, json_process_left_lane,
                       json_process_right_lane, json_right_lane, json_sec_left_lane, json_sec_right_lane,
                       json_has_secondary, json_speed, json_steering)

    return json_data
    # endregion

# endregion

# region User config ----------------------------------------------------------------------

CONFIG_FILE = "config.json"

def load_config():
    """Loads saved configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}


def save_config(config):
    """Saves configuration to config.json."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


def extract_base_name(filename):
    """Extracts the base name from the video file, excluding description and extension."""
    match = re.match(r"(CLIP-v\d+\.\d+\.\d+-LR\d+-SLR-?\d+-MP\d+)", filename)
    return match.group(1) if match else None


def use_zenity():
    """Returns True if Zenity (GNOME file picker) is available."""
    return platform.system() == "Linux" and subprocess.run(["which", "zenity"], stdout=subprocess.PIPE).returncode == 0


def zenity_file_picker(title, initial_dir, file_filter):
    """Uses Zenity to open a native file picker on GNOME/KDE."""
    cmd = ["zenity", "--file-selection", "--title", title, "--filename", f"{initial_dir}/"]
    if file_filter:
        cmd += ["--file-filter", f"{file_filter} | {file_filter}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def select_video_file(last_path="", last_file=""):
    """Selects a video file using Zenity (Linux) or Tkinter (Windows/macOS)."""
    initial_dir = last_path if os.path.exists(last_path) else os.getcwd()

    if use_zenity():
        return zenity_file_picker("Select Video File", initial_dir, "*.mp4")

    Tk().withdraw()  # Hide root Tk window
    return filedialog.askopenfilename(
        title="Select Video File",
        initialdir=initial_dir,
        initialfile=last_file,
        filetypes=[("MP4 Files", "*.mp4")],
    )


def select_json_file(directory, base_name):
    """Selects a JSON file, filtering by base name using Tkinter."""
    if os.path.exists(directory):
        initial_dir = os.path.join(directory, "Processed")
    else:
        initial_dir = os.getcwd()

    matching_json_files = [
        f for f in os.listdir(initial_dir)
        if f.endswith(".json") and f.startswith(base_name)
    ]
    print(matching_json_files)
    if not matching_json_files:  # If no matching JSON files exist, return empty
        return ""

    Tk().withdraw()
    filetypes = [(f"{base_name} JSON Files", matching_json_files)] if matching_json_files else [
        ("JSON Files", "*.json")]

    return filedialog.askopenfilename(
        title="Select JSON File (Optional)",
        initialdir=initial_dir,
        filetypes=filetypes,
    )


# endregion

def start():
    """
        Initializes and starts the video processing pipeline.

        This function configures the algorithms for lane recognition and movement
        parameter calculation, sets the input and output video paths, and processes
        the video frame by frame.

        Configuration Details:
        - main_lane_recognition_name: str
            Name of the primary lane recognition algorithm.
        - secondary_lane_recognition_name: str
            Name of the secondary lane recognition algorithm.
        - movement_params_name: str
            Name of the movement parameter algorithm.
        - version: str
            Version identifier for the processing pipeline.
        - input_path: str
            Directory containing the input video file. Must end with a forward slash ('/') or backslash ('\\').
        - video_name: str
            Name of the input video file, including its extension.

        Procedure:
        1. Sets up instances of the lane recognition and movement parameter algorithms.
        2. Constructs the input and output video file paths.
        3. Processes the video, applying lane detection, movement calculations, and visualizations.

        Note:
        - Ensure the input path and video name are correctly configured for the environment.
        - Input video file must be in the specified input directory and have a valid format (e.g., ".mp4").
    """
    pixel_getter = get_pixel_getter('virtual_cam')  # Do NOT change
    main_lane_recognition, secondary_lane_recognition = setup_lane_recognition(pixel_getter, get_lane_recognition_instance)
    movement_params = setup_movement_params(get_movement_params_instance)

    # region Config

    # Load or initialize config
    config = load_config()
    last_used_path = config.get("input_path", "")
    last_video = config.get("video_name", "")
    last_json = config.get("json_input", "")

    # Let the user select a video
    video_file = select_video_file(last_used_path, last_video)
    if video_file:
        input_path = os.path.dirname(video_file)
        video_name = os.path.basename(video_file)
        config["input_path"] = input_path
        config["video_name"] = video_name
    else:
        input_path = last_used_path
        video_name = last_video

    # Extract base name for JSON filtering
    base_name = extract_base_name(video_name)

    # Let the user select an optional JSON file
    json_input = select_json_file(input_path, base_name) if video_file else last_json
    config["json_input"] = json_input

    # Save updated config
    save_config(config)

    # endregion

    # region setup
    base_name = generate_base_name(get_lane_recognition_id, get_movement_params_id)
    input_video, output_video = set_input_and_output(input_path, video_name, base_name)

    json_output_path = output_video.replace(".avi", ".json")
    set_json_path(json_input, json_output_path)
    # endregion

    # Process video
    load_video(main_lane_recognition, secondary_lane_recognition, movement_params, input_video, output_video)

start()