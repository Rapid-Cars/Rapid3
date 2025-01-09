import cv2
import os

from Software.Camera.lane_recognition import *
from Software.Camera.movement_params import *

HEIGHT = 240
WIDTH = 320

# region Debug visualisations -------------------------------------------------------------

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


def get_ignore_zone(img):
    """
        Determines the ignore zone of the given image.
        The ignore zone is a zone in the image where the car is visible and where the lane recognition
        is therefore unreliable.
        The zone is determined by checking for brightness changes

        Parameters:
        - img: ndarray
            Grayscale image for processing.

        Returns:
        - tuple: (x_min, y_min, x_max, y_max) specifying the ignore zone's rectangle.
    """
    y_min = HEIGHT
    y_max = HEIGHT
    x_min = 85
    x_max = WIDTH - 55

    for y in range(HEIGHT - 20, 0, -5):
        first_pixel = img[y, WIDTH // 2]
        second_pixel = img[y + 5, WIDTH // 2]
        if first_pixel > second_pixel:
            dif = first_pixel - second_pixel
        else:
            dif = second_pixel - first_pixel
        if dif > 15 and second_pixel < 60:
            y_min = y
            break


    return x_min, y_min, x_max, y_max


def draw_ignore_zone(img, grayscale_image):
    """
        Draws a rectangle on the image to represent the ignore zone.

        Parameters:
        - img: ndarray
            The image on which to draw the ignore zone.
        - grayscale_image: ndarray
            Grayscale version of the image used to determine the ignore zone.
    """
    x_min, y_min, x_max, y_max = get_ignore_zone(grayscale_image)
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


def draw_movement_params(img, vehicle_speed, steering_angle):
    """
        Draws visual indicators for vehicle speed and steering angle on the given image.

        Parameters:
        - img: ndarray
            The image on which to draw the indicators.
        - vehicle_speed: int
            The speed of the vehicle (0-100).
        - steering_angle: int
            The steering angle (0-100, 50=neutral).
    """
    draw_speed(img, vehicle_speed)
    draw_steering(img, steering_angle)


def draw_speed(img, vehicle_speed):
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
    x_position = 10

    # Draws background line to indicate the full speed range
    cv2.line(img, (x_position, line_base_y), (x_position, max_line_end_y), (50, 50, 50), 3)

    # Draws the line to represent the calculated speed
    line_length = int(max_line_length * (vehicle_speed / 100))
    line_end_y = line_base_y - line_length
    cv2.line(img, (x_position, line_base_y), (x_position, line_end_y), (0, 0, 255), 1)


def draw_steering(img, steering_angle):
    """
    Draws a horizontal red line on the given image to represent steering angle.
    The line is drawn on the bottom of the image with the start position in the horizontal middle.
    Its direction and length is proportional to the given steering angle.

    Parameters:
    - img: ndarray (color image)
    - steering_angle: int (0-100, 50=neutral)
    """
    line_base_x = 20
    max_line_length = (WIDTH - 40) // 2
    max_line_end_x = line_base_x + max_line_length * 2
    y_position = HEIGHT - 20

    # Draws background line to indicate the full steering range
    cv2.line(img, (line_base_x, y_position), (max_line_end_x, y_position), (50, 50, 50), 3)

    line_start_x = WIDTH // 2
    line_length = int(max_line_length * (steering_angle - 50) / 100)
    line_end_x = line_start_x + line_length

    cv2.line(img, (line_start_x, y_position), (line_end_x, y_position), (0, 0, 255), 1)

# endregion

# region File name handling ---------------------------------------------------------------

def generate_base_name(version, lane_algorithm_name, secondary_lane_algorithm_name, movement_algorithm_name):
    """
        Generates a standardized base name for the video file based on the version
        and the selected algorithms for lane recognition and movement parameters.

        Parameters:
        - version: str
            Version identifier for the processing pipeline.
        - lane_algorithm_name: str
            Name of the primary lane recognition algorithm.
        - secondary_lane_algorithm_name: str
            Name of the secondary lane recognition algorithm.
        - movement_algorithm_name: str
            Name of the movement parameter algorithm.

        Returns:
        - str: A formatted base name string in the form:
            "v{version}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"

        Raises:
        - ValueError: If any provided algorithm name is invalid.
    """
    lane_recognition_id = {
        "BaseInitiatedLaneFinder": 0,
        "CenterLaneFinder": 1,
        "BaseContrastFinder": 2,
        "BaseInitMarc": 3
    }.get(lane_algorithm_name, -1)  # Default to -1 if not found
    secondary_lane_recognition_id = {
        "BaseInitiatedLaneFinder": 0,
        "CenterLaneFinder": 1,
        "BaseContrastFinder": 2,
        "BaseInitMarc": 3
    }.get(secondary_lane_algorithm_name, -1)  # Default to -1 if not found

    movement_algorithm_id = {
        "CenterDeviationDriver": 0,
        "DominantLaneAngleDriver": 1,
        "AverageAngleDriver": 2,
    }.get(movement_algorithm_name, -1)  # Default to -1 if not found

    if lane_recognition_id == -1 or movement_algorithm_id == -1:
        raise ValueError("Invalid algorithm name provided.")

    # Generate the base name
    base_name = f"v{version}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"
    return base_name


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
    input_video = os.path.join(input_path, video_name)
    print("Processing: ", input_video)

    # Remove the extension from video_name
    base_name = os.path.splitext(video_name)[0]
    output_video = os.path.join(input_path, "Processed", f"{base_name} - Processed with {processing_name}.avi")

    print("Saving output to: ", output_video)
    return input_video, output_video

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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        process_frame(frame, main_lane_recognition, secondary_lane_recognition, movement_params)
        out.write(frame)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


LAST_LEFT_LANE = []
LAST_RIGHT_LANE = []
LAST_LEFT_COUNT = 0
LAST_RIGHT_COUNT = 0


def process_frame(img, main_lane_recognition, secondary_lane_recognition, movement_params):
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
    left_lane, right_lane = main_lane_recognition.recognize_lanes(gray)
    process_left_lane = left_lane
    process_right_lane = right_lane
    if secondary_lane_recognition:
        sec_left_lane, sec_right_lane = secondary_lane_recognition.recognize_lanes(gray)
        # Use secondary algorithm if a lane is empty
        if not left_lane or not right_lane:
            sec_left_lane, sec_right_lane = secondary_lane_recognition.recognize_lanes(gray)
            if len(sec_left_lane) > len(left_lane):
                process_left_lane = sec_left_lane
            if len(sec_right_lane) > len(right_lane):
                process_right_lane = sec_right_lane


    # If a lane is still empty the last recorded lane will be used instead
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

    speed, steering = movement_params.get_movement_params(process_left_lane, process_right_lane)

    # region Draws the debug visualizations
    # Draws the searchable area of the algorithm
    draw_search_area(img, main_lane_recognition) # NOT Implemented yet

    # Draws the ignore zone (zone where the car is visible
    #draw_ignore_zone(img, gray)

    # Draws the found lane markings
    draw_lanes(img, left_lane, right_lane, 5, (255, 0, 0), (0, 255, 0), 1)
    if secondary_lane_recognition:
        draw_lanes(img, sec_left_lane, sec_right_lane, 5, (200, 0, 200), (0, 200, 200), 1)
    draw_lanes(img, process_left_lane, process_right_lane, 2, (100, 0, 255), (0, 100, 255), -1)

    # Draws the speed and steering value of the car
    draw_speed(img, speed)
    draw_steering(img, steering)
    # endregion
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
    main_lane_recognition_name = "BaseInitMarc"
    secondary_lane_recognition_name = "None"
    movement_params_name = "DominantLaneAngleDriver"

    version = "0.1.18"
    """
    Note for input_path:
    - The input path is specific to each user
    - On Windows use "\\" instead of "/" to mark a directory
    - The input path must end with "\\" or "/"
    - There has to be a separate directory for the output video file in the input directory.
      - This directory must be named "Processed"
    - 
    
    Note for video_name:
    - The file must be in the directory specified by input_path
    - The file extension must be ".mp4"
    - You must include the file extension
    """
    input_path = "/home/robmroi/Downloads/Clips/" # Specific to user
    video_name = "CLIP-v0.1.17-LR1-SLR2-MP0_00001" + ".mp4" # Enter the name of the video file here
    base_name = generate_base_name(version, main_lane_recognition_name, secondary_lane_recognition_name, movement_params_name)
    input_video, output_video = set_input_and_output(input_path, video_name, base_name)

    # Setup lane recognition and movement calculation algorithms
    pixel_getter = get_pixel_getter('virtual_cam') # Do NOT change
    main_lane_recognition = get_lane_recognition_instance(main_lane_recognition_name)
    main_lane_recognition.setup(pixel_getter)
    secondary_lane_recognition = get_lane_recognition_instance(secondary_lane_recognition_name)
    if secondary_lane_recognition:
        secondary_lane_recognition.setup(pixel_getter)
    movement_params = get_movement_params_instance(movement_params_name)

    # Process video
    load_video(main_lane_recognition, secondary_lane_recognition, movement_params, input_video, output_video)

start()