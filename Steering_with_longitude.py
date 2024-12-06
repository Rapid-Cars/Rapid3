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
speed and steering through two given x and y coordinates EDGES1 SHOULD BE DESIGNED TO BREAK AFTER EVERY X
"""

def find_border(img):
    edges1 = []
    edges2 = []
    writing_to_x_edges2 = False  # Flag to track which array to write to

    for x in range(10, 320, 10):  # crossing of longitude
        #img.draw_line(x, 0, x, 240, 5, color=255)
        for y in range(10, 230):  # set 10 higher, because vision worsens in the distance
            if img.get_pixel(x, y) == 255:  # white because inversion
                if not writing_to_x_edges2:
                    edges1.append((x, y))
                    break
                else:
                    edges2.append((x,y))
            else:
                if writing_to_x_edges2 == False and len(edges1) > 0:
                    writing_to_x_edges2 = True

    #print("edges1: ", edges1)
    #print("\n")
    #print("edges2: ", edges2)

    if len(edges2) > len(edges1):
        edges1, edges2 = edges2, edges1

    angle = 0
    speed = 0

    #print("edges1: ", edges1)
    #print("\n")
    #print("edges2: ", edges2)
    #print("\n")

    img.draw_circle(edges1[-1][1], edges1[-1][0], 15, color=255)
    img.draw_circle(edges1[0][1], edges1[0][0], 15, color=255)

    if len(edges1) >= 2 and edges1[-1][1]-edges1[0][1] != 0:     #calulate the steering with the arctan [x][y]
        angle = math.atan((edges1[-1][0]-edges1[0][0]) / (edges1[-1][1]-edges1[0][1]))
        coefficient = angle * 2 / 3.1459

        steering =  50 * (1 + coefficient)
        speed = 100
        #steering = 50
    else:
        speed = 0
        #speed = 100
        steering = 50
    print("steering:", steering, " speed:", speed, " angle:", angle*180/3.1459, "°")
    #print(angle)
    return speed, steering, angle

def draw_arrow(img, speed, steering, angle):

    base_x = 160  # Center of the image horizontally
    base_y = 230  # Bottom of the image

    # Calculate arrow length and direction
    max_length = 200  # Maximum arrow length
    arrow_length = int((speed / 100) * max_length)

    # Calculate arrow tip coordinates
    tip_x = int(base_x + arrow_length * math.sin(angle))  # Horizontal deviation
    tip_y = int(base_y - arrow_length * math.cos(angle))  # Vertical length

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
