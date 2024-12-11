import cv2
import numpy as np

from Software.Camera.lane_recognition import *
from Software.Camera.movement_params import *

HEIGHT = 240
WIDTH = 320

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
                    "Video 1 45 rechts", "Video 1", "Test - Oval - Linksrum", "Kreuzung", "Test - Oval - Rechtsrum", "Oval im Raum", "Wasserzeichen"] # 0 - 11
    input_video = input_path + input_videos[selected_video] + ".mp4"  # Path to video + video name
    print("Processing: ", input_video)

    output_path = "/home/robin/NextUP/NXP/Videos/Output/" # Path to output
    output = output_path + input_videos[selected_video] + " - processed.avi"

    return input_video, output


def load_video(lane_recognizer, movement_params, video = 0):
    """
    Load and process a video using OpenCV.

    This function initializes the video capture and writer objects, reads
    frames from an input video, processes each frame, and writes the
    processed frames to an output video file. It also displays each frame
    in a window until the video ends or the user closes the window.
    """
    input_vid, output = set_input_and_output(video)

    cap = cv2.VideoCapture(input_vid)
    # noinspection PyUnresolvedReferences
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output, fourcc, 30.0, (320, 240))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        process_frame(frame, lane_recognizer, movement_params)
        out.write(frame)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def process_frame(img, lane_recognizer, movement_params):
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
    based on the recognized lanes. Additionally, if visuals are enabled,
    it draws lane lines, centers, deviations, speed, and steering angle
    on the frame for visualization purposes.
    """
    global HEIGHT, WIDTH
    HEIGHT, WIDTH = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    left_lane, right_lane = lane_recognizer.recognize_lanes(gray)
    # Process video
    speed, steering = movement_params.get_movement_params(left_lane, right_lane)

    visuals = True # True to draw visuals on the screen, false if no visuals are needed

    if visuals:
        # Draw left border
        if left_lane:
            for element in left_lane:
                if element is not None:
                    cv2.circle(img, (element[1], element[0]), CIRCLE_RADIUS, (255, 0, 0), LINE_THICKNESS)
        if right_lane:
            for element in right_lane:
                if element is not None:
                    cv2.circle(img, (element[1], element[0]), CIRCLE_RADIUS, (255, 0, 0), LINE_THICKNESS)

        # Draw speed and steering
        # Draws the border, speed and the steering angle on the frame
        draw_speed(img, speed)
        draw_steering(img, steering)


def start():
    pixel_getter = get_pixel_getter('virtual_cam')
    lane_recognition = get_lane_recognition_instance('CenterLineFinder')
    lane_recognition.setup(pixel_getter)
    movement_params = get_movement_params_instance('MovementParamsOne')
    load_video(lane_recognition, movement_params, 0)

start()