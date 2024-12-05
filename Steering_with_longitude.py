# Untitled - By: maisb - Thu Dec 5 2024

import sensor
import time
import math

# Camera initialization
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # Grayscale mode
sensor.set_framesize(sensor.QVGA)  # 320x240 pixels
sensor.skip_frames(time=2000)  # Time to stabilize the camera
sensor.set_auto_gain(False)  # Disable automatic exposure
sensor.set_auto_whitebal(False)  # Disable automatic white balance
clock = time.clock()
THRESHOLD = 80  # Brightness threshold to detect dark pixels (0-255)
"""
The following program uses the idea of drawing "longitudes" through the image and calculate the
speed and steering through two given x and y coordinates
"""

def find_border(img):
    x_edges = []

    for x in range (0, 320, 10):            #crossing of longitude
        for y in range (0, 240):
            if img.get_pixel(x, y) == 255:  #white cause inversion
                print("There is something at ", x, y) #helps debugging
                x_edges.append((x, y))

    value_count = {}

    for row in x_edges:
        # Only consider the first entry of each row
        value = row[0]  # First value of each row
        if value in value_count:
            value_count[value] += 1
        else:
            value_count[value] = 1

    # Step 2: Classify values into lane1 and lane2 based on their occurrences
    lane_above = []  # For values that appear exactly once
    #lane_below = []  # For values that appear exactly twice

    seen = set()  # To track the first occurrence of the first value
    lane_above = []   # To store the tuples with first-time first values

    for row in x_edges:
        first_value = row[0]
        if first_value not in seen:  # If the first value is seen for the first time
            lane_above.append(row)  # Add the tuple to the result
            seen.add(first_value)  # Mark this first value as seen


    steering_factors = []
    speed = 0

    if len(lane_above) < 3:     #calulate the steering with the arctan [x][y]
        coefficient = 1-math.atan(lane_above[0][0]-lane_above[-1][0] / lane_above[0][1]-lane_above[-1][1])*2/3.1459

        steering_factors.append(coefficient * 50)
        steering = sum(steering_factors) / len(steering_factors)
        steering = max(0, min(100, steering))
        speed = 100
    else:
        speed = 0
        steering = 50

    return speed, steering

def draw_arrow(img, speed, steering):
    img_width = img.width()
    img_height = img.height()

    base_x = img_width // 2  # Center of the image horizontally
    base_y = img_height - 10  # Bottom of the image

    # Calculate arrow length and direction
    max_length = 200  # Maximum arrow length
    arrow_length = int((speed / 100) * max_length)

    # Steering angle (0 = 45° left, 50 = vertical, 100 = 45° right)
    angle_offset = (steering - 50) * 0.45  # Map to degrees
    angle_radians = angle_offset * (3.14159 / 180)  # Convert to radians

    # Calculate arrow tip coordinates
    tip_x = int(base_x + arrow_length * -angle_radians)  # Horizontal deviation
    tip_y = int(base_y - arrow_length)  # Vertical length

    # Draw the arrow on the image
    img.draw_arrow(base_x, base_y, tip_x, tip_y, color=255, thickness=4)



while True:
    clock.tick()
    img = sensor.snapshot()
    img = img.binary([(0, THRESHOLD)])  # Convert to binary image
    print(clock.fps())
    speed, steering = find_border(img)

    # Draw the arrow representing speed and steering
    draw_arrow(img, speed, steering)
