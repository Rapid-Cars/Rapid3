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
THRESHOLD = 100  # Brightness threshold to detect dark pixels (0-255)

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

while True:
    clock.tick()
    img = sensor.snapshot()  # Capture an image

    # Define the zones (top, middle, bottom)
    zones = [20, 70, 120, 170, 220]  # y-coordinates for the zones
    results = []

    for y in zones:
        left, right = find_edges(img, y)
        results.append((y, left, right))

        # Draw the results on the image
        if left:
            img.draw_circle(left, y, 5, color=255)  # Mark left edge
        if right:
            img.draw_circle(right, y, 5, color=255)  # Mark right edge

    # Output the results
    #print("Edges detected (y, left_edge, right_edge):", results)
    print(clock.fps())

    # For testing purposes only. 
    #time.sleep(1)

    # Optional: Save the image with annotations (e.g., for debugging)
    # img.save("output.jpg")
