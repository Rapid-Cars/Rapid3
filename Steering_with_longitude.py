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
THRESHOLD = 40  # Brightness threshold to detect dark pixels (0-255)
"""
The following program uses the idea of drawing "longitudes" through the image and calculate the
speed and steering through two given x and y coordinates
"""

def find_border(img):
    x_edges = []

    for x in range (10, 310, 10):            #crossing of longitude
        for y in range (10, 230):
            if img.get_pixel(x, y) == 255:  #white cause inversion
                #print("There is something at ", x, y) #helps debugging
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

    angle = 0
    speed = 0

    if len(lane_above) >= 2 and lane_above[-1][1]-lane_above[0][1] != 0:     #calulate the steering with the arctan [x][y]
        angle = math.atan(lane_above[-1][0]-lane_above[0][0] / lane_above[-1][1]-lane_above[0][1])
        coefficient = angle * 2 / 3.1459

        steering =  50 * (1 + coefficient)
        speed = 100
        #steering = 50
    else:
        speed = 0
        #speed = 100
        steering = 50
    print("steering: ", steering, "speed: ", speed, "angle: ", angle*180/3.1459, "°")
    return speed, steering, angle

def draw_arrow(img, speed, steering, angle):

    base_x = 160  # Center of the image horizontally
    base_y = 230  # Bottom of the image

    # Calculate arrow length and direction
    max_length = 200  # Maximum arrow length
    arrow_length = int((speed / 100) * max_length)

    # Calculate arrow tip coordinates
    tip_x = int(base_x + arrow_length * math.sin(angle))  # Horizontal deviation
    tip_y = int(base_y + arrow_length * math.cos(angle))  # Vertical length

    # Draw the arrow on the image
    img.draw_arrow(base_x, base_y, tip_x, tip_y, color=255, thickness=4)



while True:
    clock.tick()
    #print(clock.tick())
    img = sensor.snapshot()
    img = img.binary([(0, THRESHOLD)])  # Convert to binary image
    #print(clock.fps())
    speed, steering, angle = find_border(img)

    # Draw the arrow representing speed and steering
    draw_arrow(img, speed, steering, angle)
