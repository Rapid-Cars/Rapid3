import cv2
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
# Shared with /Software/Kamera/main.py

# Constants
CONSECUTIVE_PIXELS = 5
THRESHOLD = 70
NO_LANE_THRESHOLD = 5  # Number of elements in the edges_array for it to count as a lane

def calculate_segment_averages(arr, fraction, index):
    """
    Calculate the average of specified segments of an array. The function
    divides the input array into a given number of segments as specified
    by the 'fraction' parameter. It calculates averages for each segment
    based on the specified index of elements within the array.

    Parameters:
    arr: list
        A list of elements where each element is expected to have
        accessible elements by indexing.
    fraction: int
        A positive integer indicating the number of segments to divide
        the array into.
    index: int
        The index position to access elements within each element of
        the array for average calculation.

    Returns:
    list
        A list of averages for each calculated segment. Returns an empty
        list if the input array is empty.

    Raises:
    ValueError
        If the fraction is not a positive integer.
    """
    if not arr:  # Handle empty array
        return []

    if fraction <= 0 or not isinstance(fraction, int):
        raise ValueError("Fraction must be a positive integer.")

    length = len(arr)
    segment_size = length // fraction  # Calculate size of each segment

    indexElements = []
    for element in arr:
        indexElements.append(element[index])

    averages = []
    for i in range(fraction):
        start = i * segment_size
        end = start + segment_size if i < fraction - 1 else length
        segment = indexElements[start:end]
        avg = sum(segment) / len(segment) if segment else 0
        averages.append(avg)

    return averages


def find_border(img):
    """
    Find the borders in an image by detecting edges at specific intervals.

    This function processes the provided image by iterating over a range of
    vertical lines, spaced 10 pixels apart, starting from pixel 20 and ending
    20 pixels before the bottom of the image. For each line, it determines its
    left and right edges and stores the coordinates.

    Parameters
    ----------
    img : numpy.ndarray
        The input image in which edges are to be detected. Assumes a 2D array
        where img.shape[0] refers to the height of the image.

    Returns
    -------
    list of tuple
        A list of tuples, each containing a vertical position `y` and the
        corresponding left and right edge positions on that line (y, left, right).
    """
    edges = []
    for y in range(20, img.shape[0] - 20, 10):
        left, right = find_edges(img, y)
        edges.append((y, left, right))
    return edges


def find_edges(img, y, threshold=THRESHOLD, consecutive_pixels=CONSECUTIVE_PIXELS):
    """
    Finds the left and right edges on a given row of an image based on pixel intensity
    and a specified threshold.

    The function analyzes a specific row, defined by 'y', of the image and looks for the
    first and last series of consecutive pixels that have intensity values below the
    specified threshold. The search begins from the center of the row moving towards
    both ends. It identifies the left and right edges where a series of consecutive
    pixels, indicating the potential edge, is found.

    Parameters:
        img (array-like): A 2D array representing the image where the edges need to be found.
        y (int): The row index in the image where the edge detection is performed.
        threshold: int = THRESHOLD: The intensity threshold below which pixels are considered part of an edge.
        consecutive_pixels: int = CONSECUTIVE_PIXELS: The number of consecutive pixels below the
            threshold needed to determine an edge.

    Returns:
        tuple: A tuple containing the left and right edge positions on the specified row. The
        left edge is returned first, followed by the right edge.
    """
    height, width = img.shape
    mid_x = width // 2

    left_edge = 0
    consecutive_count = 0
    for x in range(mid_x, 0, -1):
        if img[y, x] < threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_pixels:
                left_edge = x + (consecutive_pixels // 2)
                break
        else:
            consecutive_count = 0

    right_edge = None
    consecutive_count = 0
    for x in range(mid_x, width):
        if img[y, x] < threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_pixels:
                right_edge = x - (consecutive_pixels // 2)
                break
        else:
            consecutive_count = 0

    return left_edge, right_edge


def calculate_speed_and_steering(edges):
    """
    Calculate the speed and steering based on the detected road edges. This function processes the input list of edges,
    determines their validity, and calculates appropriate speed and steering values to navigate based on the road conditions.

    Parameters:
    edges : list
        A list of tuples, where each tuple represents an edge detected on the road. Each tuple contains information about
        the edge and its corresponding left and right positions.

    Returns:
    tuple
        A tuple containing the calculated speed and steering values. Speed indicates how fast the vehicle should move,
        while steering represents the desired steering angle from 0 to 100.
    """
    both_edges = [edge for edge in edges if edge[1] is not None and edge[2] is not None]
    left_edges = [edge for edge in edges if edge[1] is not None]
    right_edges = [edge for edge in edges if edge[2] is not None]

    # print("left: ", len(left_edges), ", right: ", len(right_edges), "; valid: ", len(both_edges))

    # Initialize speed and steering
    speed = 0
    steering = 50  # Neutral steering value

    if len(left_edges) == 0 and len(right_edges) == 0:
        # No valid edges detected -> Stop
        return 0, 50  # No road edges: speed = 0, straight steering

    # Calculate the averages of left and right edges
    if len(left_edges) == 0 or len(right_edges) == 0:
        mid_point = -1
    else:
        avg_left = sum(edge[1] for edge in left_edges) / len(left_edges)
        avg_right = sum(edge[2] for edge in right_edges) / len(right_edges)
        # Calculate the midpoint
        mid_point = (avg_left + avg_right) / 2

    # Analyze the current road
    center_deviation = (mid_point - (320 // 2)) / (320 // 2)  # Normalized deviation from the image center

    # ----- Speed Calculation -----
    if len(both_edges) < NO_LANE_THRESHOLD:
        # Very little lane markings on both sides -> Slow down
        speed = 20
    elif len(left_edges) < NO_LANE_THRESHOLD or len(right_edges) < NO_LANE_THRESHOLD:
        # One edge is missing -> Drive cautiously
        speed = 30
    else:
        # Many lane markings -> Drive fast
        speed = 50 # For now 50, this can be increased with a better algorithm

    # ----- Steering Calculation ----
    steering_factors = []
    steering_factors.append(int(50 - center_deviation * 50)) # Add the deviation from the center to the steering factors

    left_averages = calculate_segment_averages(left_edges, 3, 1)
    right_averages = calculate_segment_averages(right_edges, 3, 2)

    # Check if road is straight
    if len(left_averages) == 3:
        dif = left_averages[1] - left_averages[2]
        if (left_averages[1] + dif) == 0:
            relative = 1
        else:
            relative = left_averages[0] / (left_averages[1] + dif)
        if relative < 0.95 or relative > 1.05: # If relative is in this range, the curvature of the road is minimal
            steering_factors.append(relative * 50)
            steering_factors.append(relative * 50)

    if len(right_averages) == 3:
        dif = right_averages[1] - right_averages[2]
        if (right_averages[1] + dif) == 0:
            relative = 1
        else:
            relative = right_averages[0] / (right_averages[1] + dif)
        if relative < 0.95 or relative > 1.05: # If relative is in this range, the curvature of the road is minimal
            steering_factors.append(relative * 50)
            steering_factors.append(relative * 50)

    #print(steering_factors)
    #print(sum(steering_factors) / len(steering_factors))

    steering = sum(steering_factors) / len(steering_factors)
    steering = max(0, min(100, steering))  # Limit to 0-100

    return speed, steering


# ----------------------------------------------------------------------------------------------------------------------
# Specific to virtual_cam

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


def draw_circle(img, center_x, center_y):
    """
    Draws a small green circle on the image at the specified coordinates.

    Parameters:
    - img: ndarray
    - center_x: int
    - center_y: int
    """
    cv2.circle(img, (center_x, center_y), CIRCLE_RADIUS, GREEN_COLOR, LINE_THICKNESS)


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
    input = input_path + input_videos[selected_video] + ".mp4"  # Path to video + video name
    print("Processing: ", input)

    output_path = "/home/robin/NextUP/NXP/Videos/Output/" # Path to output
    output = output_path + input_videos[selected_video] + " - processed.avi"

    return input, output

input_vid, output = set_input_and_output(8)

cap = cv2.VideoCapture(input_vid)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output, fourcc, 30.0, (320, 240))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Process video
    border = find_border(gray)
    speed, steering = calculate_speed_and_steering(border)

    # Draws the border, speed and the steering angle on the frame
    for element in border:
        y = element[0]
        left = element[1]
        right = element[2]
        if left:
            draw_circle(frame, left, y)
        if right:
            draw_circle(frame, right, y)
    draw_speed(frame, speed)
    draw_steering(frame, steering)
    out.write(frame)

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()