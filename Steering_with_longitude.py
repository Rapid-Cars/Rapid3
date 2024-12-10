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
THRESHOLD = 60  # Brightness threshold to detect dark pixels (0-255)
DEPTH = 40      #How close to the top border should be evaluated?

"""
The following program uses the idea of drawing "longitudes" through the image and calculate the
speed and steering through two given x and y coordinates. At first, every intersection will be
saved in an array. If an intersection is found, it jumps to the next longitude. If it found an
intersection, on the next longitude(s) none, but then for some reason again, it might be because
it is the other lane. Then this should be written in a second array. We compare which array has
more intersections with the longitude (Which lane is less perpendicular in the image?) We take the
one with more intersections, calculate speed and steering with the arctan, draw an arrow and pass
everything to the microcontroller.
"""

def find_border(img):
    edges1 = []
    edges2 = []
    edges3 = []
    writing_to_edges2 = False  # Flag to track which array to write to
    writing_to_edges3 = False  # Flag to track which array to write to

    for x in range(10, 320, 10):  # crossing of longitude
        #img.draw_line(x, DEPTH, x, 240, color=255)
        found_white = False  # Track if a white pixel was found in this column
        for y in range(DEPTH, 240):  # Higher start due to worse vision in the distance
            if img.get_pixel(x, y) == 255:  # White pixel due to inversion
                found_white = True
                if not writing_to_edges2 and not writing_to_edges3:
                    edges1.append((x, y))
                elif not writing_to_edges3:
                    edges2.append((x, y))
                else:
                    edges3.append((x, y))
                break
        if not found_white and not writing_to_edges2 and len(edges1) > 0:
            writing_to_edges2 = True
        if not found_white and not writing_to_edges3 and len(edges2) > 0:
            writing_to_edges3 = True


    #print("\nedges1: ", edges1)
    #print("edges2: ", edges2)

    longest_array = max([edges1, edges2, edges3], key=len)

    angle = 0
    speed = 0

    #print("longest_array: ", longest_array)

    if len(edges1) >= 2 and longest_array[-1][1]-longest_array[0][1] != 0:     #calulate the steering with the arctan [x][y]
        img.draw_circle(longest_array[-1][0], longest_array[-1][1], 15, color=255)
        img.draw_circle(longest_array[0][0], longest_array[0][1], 15, color=255)
        angle = math.atan((longest_array[-1][0]-longest_array[0][0]) / (longest_array[-1][1]-longest_array[0][1]))
        coefficient = angle * 2 / 3.1459

        steering =  50 * (1 + coefficient)
        speed = 100
        #steering = 50
    else:
        speed = 0
        #speed = 100
        steering = 50
    print("steering:", steering, " speed:", speed, " angle:", angle*180/3.1459, "°")
    #print("angle: ", angle)
    return speed, steering, angle

def draw_arrow(img, speed, steering, angle):

    base_x = 160  # Center of the image horizontally
    base_y = 230  # Bottom of the image

    # Calculate arrow length and direction
    max_length = 200  # Maximum arrow length
    arrow_length = int((speed / 100) * max_length)

    # Calculate arrow tip coordinates
    tip_x = int(base_x - arrow_length * math.sin(angle))  # Horizontal deviation
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
