import cv2
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
# Shared with /Software/Kamera/main.py

# Constants
CONSECUTIVE_PIXELS = 5 # Number of pixels in a row for it to count as an edge
MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5 # If the consecutive pixels exceed this value it won't be counted as a lane
THRESHOLD = 70 # Darkness Threshold, can be a constant but can also change dynamically
HEIGHT = 240
WIDTH = 320

# Border recognition
# ///////////////////////////////////////////////////////////////////

def set_threshold():
    """Sets the threshold dynamically based on the image. Dummy function."""
    return


def get_border_element(img, x, y, from_left = 1):
    """
    Finds the border element in a given row of an image by scanning horizontally
    from a given starting point. It detects the border by counting consecutive
    pixels below a predefined intensity threshold. If a sufficient number of
    consecutive low-intensity pixels are found, it identifies this as a border
    element and computes its middle point. If there are to many consecutive
    intensity pixels, it returns None.

    Parameters:
        img: int[][] - A 2D array representing the grayscale image.
        x: int - The initial horizontal position to start scanning.
        y: int - The vertical row to be scanned for the border element.
        from_left: int - The direction to scan; 1 for left to right, -1 for right to left.

    Returns:
        tuple[int, int] | None: The (y, x) coordinates of the border element's
        middle point if found, otherwise None.
    """
    element = None
    consecutive_count = 0
    first_x = None
    x_min = max(x - MAX_CONSECUTIVE_PIXELS - 10, 0)
    x_max = min(x + MAX_CONSECUTIVE_PIXELS + 10, WIDTH - 1)
    if from_left == 1:
        rng = range(x_min, x_max, 1)
    else:
        rng = range(x_max, x_min, -1)
    for x in rng:
        if img[y, x] < THRESHOLD:
            consecutive_count += 1
            if consecutive_count >= CONSECUTIVE_PIXELS:
                if not first_x:
                    first_x = x
        else:
            consecutive_count = 0

    if consecutive_count < MAX_CONSECUTIVE_PIXELS and first_x is not None:
        # Calculate the middle point of the element
        element =(y, (2 * first_x + consecutive_count) // 2)
    return element


def get_lane_start(img):
    """
    Determine the start positions of left and right lanes in the given image.
    The function searches for the starting points of the left and right lanes
    by scanning the image within defined regions and directions. It returns the
    first detected lane start positions for both left and right lanes.

    Parameters:
        img: A 2D or 3D array representing the image data in which the lanes
             are to be detected.

    Returns:
        A tuple (left_lane_start, right_lane_start), where both elements
        represent the starting points of the left and right lanes respectively.
        These positions are derived from scanning the image according to
        specified parameters for x and y coordinates.
    """
    # Find left lane
    # Search params:
    # x: 10 to (width // 2) - 10
    # y: Start at height - 10 then move to height // 2
    left_lane_start = None
    for y in range(HEIGHT - 10, HEIGHT // 2, -10):
        x = 20
        while x < ((WIDTH // 2) - (2 * MAX_CONSECUTIVE_PIXELS - 10)):
            x += MAX_CONSECUTIVE_PIXELS
            element = get_border_element(img, x, y, -1)
            if element:
                left_lane_start = element
                break
        if left_lane_start: break

    # Search params:
    # x: (width // 2) + 10 to width - 10
    # y: Start at height - 10 then move to height // 2
    right_lane_start = None
    for y in range(HEIGHT - 10, HEIGHT // 2, -10):
        x = WIDTH - 20
        while x > ((WIDTH // 2) + (2 * MAX_CONSECUTIVE_PIXELS - 10)):
            x -= MAX_CONSECUTIVE_PIXELS
            element = get_border_element(img, x, y, 1)  # Change scan direction
            if element:
                right_lane_start = element
                break
        if right_lane_start: break

    return left_lane_start, right_lane_start


def get_borders(img):
    """
    Extracts the borders of lanes from an image by finding sequential elements
    in each lane starting from the initial positions returned by get_lane_start.
    Traverses in an upward direction along the image, alternating between
    adding elements to the left and right border lists.

    Parameters:
        img: The image data from which lane borders are to be determined.

    Returns:
        A tuple containing two lists. The first list is the left border,
        and the second list is the right border. Each list contains tuples
        of coordinates (y, x) representing the borders of the lanes.
    """
    left_border = []
    right_border = []

    left_start, right_start = get_lane_start(img)

    if left_start is not None:
        x = left_start[1]
        for y in range(left_start[0], 20, -10):
            element = get_border_element(img, x, y, -1)
            if not element:
                break
            x = element[1]
            left_border.append((y, x))

    if right_start is not None:
        x = right_start[1]
        for y in range(right_start[0], 20, -10):
            element = get_border_element(img, x, y, 1)
            if not element:
                break
            x = element[1]
            right_border.append((y, x))

    return left_border, right_border


# Calculation of speed and steering
# ///////////////////////////////////////////////////////////////////

def calculate_deviation(left_border, right_border):
    """
    Calculate the deviation from the center position within a specified width.

    This function computes how far a point, defined by its left and right borders,
    is deviated from the central position within the given width. It is helpful in
    determining how centered a position is relative to its boundaries. The deviation
    is calculated as a proportion of the width.

    Parameters:
    width: int
        The total width within which the deviation is calculated. The width should
        be a positive integer.
    left_border: int
        The coordinate of the left border of the position. It should be a non-negative
        integer that does not exceed width.
    right_border: int
        The coordinate of the right border of the position. It should be a non-negative
        integer that does not exceed width and should be greater than or equal to
        the left border.

    Returns:
    float
        The deviation from the center as a value between -1 and 1. A negative value
        indicates left deviation, zero indicates center alignment, and a positive
        value indicates right deviation.
    """
    return ((WIDTH // 2) - ((left_border + right_border) / 2)) / (WIDTH // 2)


def calculate_center_deviations(left_lane, right_lane):
    deviations = []

    left_index, right_index = 0, 0
    left_border_len = len(left_lane)
    right_border_len = len(right_lane)

    while left_index < left_border_len and right_index < right_border_len:
        left_y, left_x = left_lane[left_index]
        right_y, right_x = right_lane[right_index]

        if left_y > right_y:
            # Different action when left y > right y
            # Implement your specific action here
            deviations.append((left_y, calculate_deviation(left_x, WIDTH)))
            left_index += 1
        elif right_y > left_y:
            # Different action when right y > left y
            # Implement your specific action here
            deviations.append((left_y, calculate_deviation( 0, right_x)))
            right_index += 1
        else:
            # Compare the x values when y is identical
            deviations.append((left_y, calculate_deviation(left_x, right_x)))
            left_index += 1
            right_index += 1

    # Handle any remaining left y values with no matching right y.
    while left_index < left_border_len:
        left_y, left_x = left_lane[left_index]
        deviations.append((left_y, calculate_deviation(left_x, WIDTH + 100)))
        left_index += 1

    # Handle any remaining right y values with no matching left y.
    while right_index < right_border_len:
        right_y, right_x = right_lane[right_index]
        deviations.append((right_y, calculate_deviation(-100, right_x)))
        right_index += 1

    return deviations


def calculate_movement_params(img):
    """
    Calculates movement parameters for an image-based navigation system. The function
    analyzes the given image to determine the necessary speed and steering adjustments
    required to align with detected edges or boundaries within the image. When no edges
    are detected, default movement parameters are returned. It visually annotates the image
    canvas with debug information indicating detected edges, the calculated deviation, and the
    image center.

    Parameters:
        img: ndarray
            The input image in which movement parameters are to be calculated.

    Returns:
        tuple: A tuple containing:
            - calculated_speed (int): The speed required for movement based on the
              calculated deviation from the center.
            - calculated_steering (int): The steering adjustment necessary based on the
              position of detected edges within the image.
    """
    calculated_speed = 5
    calculated_steering = 50

    left_border, right_border = get_borders(img)
    if not left_border and not right_border:
        return calculated_speed, calculated_steering

    center_deviations = calculate_center_deviations(left_border, right_border)
    average_deviation = 0
    for deviation in center_deviations:
        average_deviation += deviation[1]
    average_deviation = average_deviation / len(center_deviations)

    calculated_steering = int(50 - average_deviation * 50)

    calculated_speed = int((1 - abs(average_deviation)) * 100)
    return calculated_speed, calculated_steering


# ----------------------------------------------------------------------------------------------------------------------
# Debug visualisations

# Constants for colors and drawing
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
LINE_THICKNESS = 2
CIRCLE_RADIUS = 5

def draw_speed(img, vehicle_speed):
    """
    Draws a vertical red line on the given image to represent speed.
    The line is drawn on the left side of the image and its length is
    proportional to the given speed (0 to 100).

    Parameters:
    - img: ndarray (color image)
    - speed: int (0-100)
    """
    height, _ = img.shape[:2]
    line_base_y = height - 20
    line_length = int((height - 40) * (vehicle_speed / 100))
    line_end_y = line_base_y - line_length
    x_position = 20
    cv2.line(img, (x_position, line_base_y), (x_position, line_end_y), RED_COLOR, LINE_THICKNESS)


def draw_steering(img, steering_angle):
    """
    Draws a steering arrow on the image to represent the steering angle.

    Parameters:
    - img: ndarray (color image)
    - steering_angle: int (0-100, 50=neutral)
    """
    height, width = img.shape[:2]
    arrow_start_x = width // 2
    arrow_base_y = height - 20
    arrow_length = int(height - 40)
    angle_offset_radians = np.deg2rad((steering_angle - 50) * 0.45)
    arrow_tip_x = int(arrow_start_x + arrow_length * np.sin(angle_offset_radians))
    arrow_tip_y = int(arrow_base_y - arrow_length * np.cos(angle_offset_radians))
    cv2.arrowedLine(img, (arrow_start_x, arrow_base_y), (arrow_tip_x, arrow_tip_y), RED_COLOR, LINE_THICKNESS)


# ----------------------------------------------------------------------------------------------------------------------
# Specific to virtual_cam.py

def set_input_and_output(selected_video):
    """
    Sets the input and output paths for a selected video file and returns the
    paths as strings. This function concatenates a predefined input path with a
    list of video names, indexed by the selected video. The output path is also
    constructed similarly by appending a processed suffix to the input video name.

    Parameters:
        selected_video (int): The index of the selected video in the list of input
        videos.

    Returns:
        tuple[str, str]: A tuple containing the full path of the input video and
        the full path of the output video.
    """
    input_path = "/home/robin/NextUP/NXP/Videos/" # Path to video file
    input_videos = ["Schikane mitlaeufig", "Schikane gegenlaeufig", "Schikane gerade", "Video 2", "Video 1 45 links",
                    "Video 1 45 rechts", "Video 1", "Test - Oval - Linksrum", "Kreuzung", "Test - Oval - Rechtsrum"]
    input_video = input_path + input_videos[selected_video] + ".mp4"  # Path to video + video name
    print("Processing: ", input_video)

    output_path = "/home/robin/NextUP/NXP/Videos/Output/" # Path to output
    output = output_path + input_videos[selected_video] + " - processed.avi"

    return input_video, output

def load_video():
    """
    Load and process a video using OpenCV.

    This function initializes the video capture and writer objects, reads
    frames from an input video, processes each frame, and writes the
    processed frames to an output video file. It also displays each frame
    in a window until the video ends or the user closes the window.
    """
    input_vid, output = set_input_and_output(6)

    cap = cv2.VideoCapture(input_vid)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output, fourcc, 30.0, (320, 240))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        process_video(frame)
        out.write(frame)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def process_video(img):
    """
    Processes a video frame by updating global dimensions, converting it to grayscale, calculating movement
    parameters, and optionally drawing visual aids such as borders, deviations, speed, and steering on the frame.

    Parameters:
        img: numpy.ndarray
            An image array representing the video frame to be processed.

    Returns:
        None
    """
    global HEIGHT, WIDTH
    HEIGHT, WIDTH = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Process video
    speed, steering = calculate_movement_params(gray)

    visuals = True # True to draw visuals on the screen, false if no visuals are needed
    if visuals:
        # Draw left border
        left_border, right_border = get_borders(gray)
        if left_border:
            for element in left_border:
                cv2.circle(img, (element[1], element[0]), CIRCLE_RADIUS, (255, 0, 0), LINE_THICKNESS)
        if right_border:
            for element in right_border:
                cv2.circle(img, (element[1], element[0]), CIRCLE_RADIUS, (255, 0, 0), LINE_THICKNESS)

        # Draw deviations
        center_deviations = calculate_center_deviations(left_border, right_border)
        cv2.line(img, (WIDTH // 2, 10), (WIDTH // 2, HEIGHT - 10), RED_COLOR, LINE_THICKNESS)  # Center line
        for deviation in center_deviations:
            deviation_line_x = int(WIDTH // 2 - deviation[1] * (WIDTH // 2))
            cv2.line(img, (deviation_line_x, deviation[0] + 10), (deviation_line_x, deviation[0] - 10),
                     GREEN_COLOR, LINE_THICKNESS)

        # Draw speed and steering
        # Draws the border, speed and the steering angle on the frame
        draw_speed(img, speed)
        draw_steering(img, steering)

load_video()