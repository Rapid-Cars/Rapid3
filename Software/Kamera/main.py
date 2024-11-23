import sensor
import time

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
THRESHOLD = 70  # Brightness threshold to detect dark pixels (0-255)

def find_edges(img, y, threshold=THRESHOLD, consecutive_pixels=CONSECUTIVE_PIXELS):
    """
    Finds edges (dark regions) in a horizontal line.
    - img: The image being analyzed.
    - y: The y-coordinate of the line.
    - threshold: Brightness threshold to detect dark pixels (0-255).
    - consecutive_pixels: Number of pixels that must be below the threshold.
    """
    width = img.width()
    mid_x = width // 2

    # Search to the left (starting from the middle)
    left_edge = None
    consecutive_count = 0

    for x in range(mid_x, 0, -1):
        if img.get_pixel(x, y) < threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_pixels:
                left_edge = x + (consecutive_pixels // 2)  # Center of the zone
                break
        else:
            consecutive_count = 0

    # Search to the right (starting from the middle)
    right_edge = None
    consecutive_count = 0

    for x in range(mid_x, width):
        if img.get_pixel(x, y) < threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_pixels:
                right_edge = x - (consecutive_pixels // 2)  # Center of the zone
                break
        else:
            consecutive_count = 0

    return left_edge, right_edge

def calculate_speed_and_steering(edges):
    """
    Calculates motor speed and steering value based on detected road edges.

    Parameters:
    - edges: List of tuples [(y, left_edge, right_edge), ...] containing edges in different zones.

    Returns:
    - speed: Motor speed (0 to 100).
    - steering: Steering (0 to 100, where 0 is fully left and 100 is fully right).
    """
    valid_edges = [edge for edge in edges if edge[1] is not None and edge[2] is not None]
    no_left = [edge for edge in edges if edge[1] is None]
    no_right = [edge for edge in edges if edge[2] is None]

    # Initialize speed and steering
    speed = 0
    steering = 50  # Neutral steering value

    if len(valid_edges) == 0:
        # No valid edges detected -> Stop
        return 0, 50  # No road edges: speed = 0, straight steering

    # Calculate the averages of left and right edges
    avg_left = sum(edge[1] for edge in valid_edges) / len(valid_edges)
    avg_right = sum(edge[2] for edge in valid_edges) / len(valid_edges)

    # Calculate the midpoint and road width
    mid_point = (avg_left + avg_right) / 2
    road_width = avg_right - avg_left

    # Analyze the current road
    center_deviation = (mid_point - (320 // 2)) / (320 // 2)  # Normalized deviation from the image center

    if road_width < 50 or len(valid_edges) < len(edges) * 0.5:
        # Intersection or very narrow road -> Slow down
        speed = 20
    elif len(no_left) > 0 or len(no_right) > 0:
        # One edge is missing -> Drive cautiously
        speed = 30
    else:
        # Straight road or normal curve
        max_deviation = max(abs(edge[1] - edge[2]) for edge in valid_edges)
        if max_deviation < 50:
            speed = 100  # Straight road -> Fast
        else:
            speed = 50  # Curve -> Slower

    # Calculate steering (0 = fully left, 100 = fully right)
    steering = int(50 + center_deviation * 50)
    steering = max(0, min(100, steering))  # Limit to 0-100

    return speed, steering

def draw_arrow(img, speed, steering):
    """
    Draws an arrow on the image to visualize speed and steering.
    - Speed determines the length of the arrow.
    - Steering determines the angle of the arrow.
    """
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
    img = sensor.snapshot()  # Capture an image

    # Define the y-zones
    zones = []
    for y in range(2,22): # The pixels/lines at the very top and bottom are ignored
            zones.append(y*10)

    edges = []

    for y in zones:
        left, right = find_edges(img, y)
        edges.append((y, left, right))

        # Draw the results on the image
        if left:
            img.draw_circle(left, y, 5, color=255)  # Mark left edge
        if right:
            img.draw_circle(right, y, 5, color=255)  # Mark right edge

    speed, steering = calculate_speed_and_steering(edges)
    print("Speed: ", speed, " Steering: ", steering)

    # Draw the arrow representing speed and steering
    draw_arrow(img, speed, steering)

    # Output the results
    #print("Edges detected (y, left_edge, right_edge):", results)
    #print(clock.fps())

    # Only for testing
    #time.sleep_ms(100)

    # Optional: Save the image with annotations (e.g., for debugging)
    # img.save("output.jpg")
