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

# Configuration
CONSECUTIVE_PIXELS = 5  # Number of consecutive pixels below the threshold
# For computer screen use 100, for real road use 70
THRESHOLD = 80  # Brightness threshold to detect dark pixels (0-255)
NO_LANE_THRESHOLD = 5  # Number of elements in the edges_array for it to count as a lane
"""
    Calculates the average of the array divided into `fraction` parts.

    Parameters:
    - arr: The array to process (can be empty).
    - fraction: The denominator specifying the number of parts (e.g., 2, 3, 4).

    Returns:
    - A list of averages for each segment, or an empty list if the array is empty.
    """
"""
def calculate_segment_averages(arr, fraction, index):
    #if not arr:  # Handle empty array
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
"""
"""
Finds edges (dark regions) in a horizontal line.
- img: The image being analyzed.
- y: The y-coordinate of the line.
- threshold: Brightness threshold to detect dark pixels (0-255).
- consecutive_pixels: Number of pixels that must be below the threshold.
- additon of turn detection, checking if there is a strip of lane in the corners of the image
    if there is, it is probably a turn. We treat turns simply as existent or not, because that
    should be enough in taking the turns
"""
def find_edges_and_turns(img, y, threshold=THRESHOLD, consecutive_pixels=CONSECUTIVE_PIXELS):
    consecutive_count = 0
    left_edge = None
    right_edge = None
    global left_turn, right_turn
    left_turn = False
    right_turn = False
    # Check for left turn
    for x in range(0, 10):                #somehow it works this way, maybe the image is mirrored
        for y_t in range(0, 20):            #looking at the very top
            if img.get_pixel(x, y_t) == 255:  # White pixel, because the image is inverted
                   #the lanes are way sharper there, we dont need consecutive_pixels
                left_turn = True
                right_turn = False
                y = 0
                print("There is a left turn")
                break
        break

    # Check for right turn
    for x in range(310, 320):                      #somehow it works this way, maybe the image is mirrored
        for y_t in range(0, 20):             #looking at the very top
            if img.get_pixel(x, y_t) == 255:  # White pixel, because the image is inverted
                      #the lanes are way sharper there, we dont need consecutive_pixels
                right_turn = True
                left_turn = False
                y = 0
                print("There is a right turn!")
                break
        break
    # Find edges if no turns are detected
    if left_turn == False and right_turn == False:  #using the steering algortihm if there are no turns
        width = img.width()
        mid_x = width // 2

        # Search to the left
        consecutive_count = 0
        for x in range(mid_x, 0, -1):
                if img.get_pixel(x, y) == 255:  # Black pixel:
                    consecutive_count += 1
                    if consecutive_count >= CONSECUTIVE_PIXELS:
                        left_edge = x + (CONSECUTIVE_PIXELS // 2)  # Center of the zone
                        break
                else:
                    consecutive_count = 0

        # Search to the right
        consecutive_count = 0
        for x in range(mid_x, width):
                if img.get_pixel(x, y) == 255:  # Black pixel
                    consecutive_count += 1
                    if consecutive_count >= CONSECUTIVE_PIXELS:
                        right_edge = x - (CONSECUTIVE_PIXELS // 2)  # Center of the zone
                        break
                    else:
                        consecutive_count = 0

    # Return edges with defaults if not found
    return left_edge, right_edge



"""
Calculates motor speed and steering value based on detected road edges.

Parameters:
- edges: List of tuples [(y, left_edge, right_edge), ...] containing edges in different zones.

Returns:
- speed: Motor speed (0 to 100).
- steering: Steering (0 to 100, where 0 is fully left and 100 is fully right).
"""
def calculate_speed_and_steering(edges):
    if left_turn == False and right_turn == False:
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
            speed = 100

        # ----- Steering Calculation ----
        steering_factors = []
        steering_factors.append(int(50 - center_deviation * 50)) # Add the deviation from the center to the steering factors

        coefficient = 1-math.atan(left_edges[0][1]-left_edges[-1][1] / left_edges[0][0]-left_edges[-1][0])*2/3.1459
        #numerator x, denominator y
        steering_factors.append(coefficient * 50)
        steering_factors.append(coefficient * 50)

        coefficient = 1-math.atan(right_edges[0][2]-right_edges[-1][2] / right_edges[0][0]-right_edges[-1][0])*2/3.1459
        steering_factors.append(coefficient * 50)
        steering_factors.append(coefficient * 50)

        print(steering_factors)
        print(sum(steering_factors) / len(steering_factors))

        steering = sum(steering_factors) / len(steering_factors) #ToDo: Remove this
        steering = sum(steering_factors) / len(steering_factors)
        steering = max(0, min(100, steering))  # Limit to 0-100
    elif left_turn == True:
        speed = 30                              #set the speed and steering to set values if there are turns
        steering = 0
    else:
        speed = 30
        steering = 100
    return speed, steering


"""
Draws an arrow on the image to visualize speed and steering.
- Speed determines the length of the arrow.
- Steering determines the angle of the arrow.
"""
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

"""
Finds the borders of the road at specific y positions.
Additionally draws circles at the found borders
"""
def find_border(img):
    # Define the y-zones
    zones = []
    for y in range(2, 22):  # The pixels/lines at the very top and bottom are ignored
        zones.append(y * 10)

    edges = []

    for y in zones:
        left, right = find_edges_and_turns(img, y)
        edges.append((y, left, right))

        # Draw the results on the image
        if left:
            img.draw_circle(left, y, 5, color=255)  # Mark left edge
        if right:
            img.draw_circle(right, y, 5, color=255)  # Mark right edge
    return edges


# main loop
while True:
    clock.tick()
    print(clock.tick())
    img = sensor.snapshot()  # Capture an image
    img = img.binary([(0, THRESHOLD)])  # Convert to binary image
    border = find_border(img)

    speed, steering = calculate_speed_and_steering(border)
    #print("Speed: ", speed, " Steering: ", steering)

    # Draw the arrow representing speed and steering
    draw_arrow(img, speed, steering)

    # Output the results
    #print("Edges detected (y, left_edge, right_edge):", results)
    #print(clock.fps())

    # Only for testing
    #time.sleep_ms(100)
