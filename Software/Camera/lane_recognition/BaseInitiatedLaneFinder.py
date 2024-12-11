# Constants
CONSECUTIVE_PIXELS = 5 # Number of pixels in a row for it to count as an edge
MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5 # If the consecutive pixels exceed this value it won't be counted as a lane
THRESHOLD = 70 # Darkness Threshold, can be a constant but can also change dynamically
HEIGHT = 240
WIDTH = 320

class BaseInitiatedLaneFinder:
    """
        A lane detection algorithm that analyzes grayscale images
        using pixel intensity values to identify lane lines.

        1. Initialization:
           - Instantiates a pixel getter object responsible for retrieving
             pixel intensity values from the image.

        2. Thresholding:
           - Establishes a dynamic threshold for pixel intensity to differentiate
             lane regions based on brightness, though currently implemented as a
             placeholder function in this code.

        3. Lane Detection:
           - Identifies starting positions for left and right lanes by scanning
             designated regions, detecting consecutive low-intensity pixels
             indicative of potential lane markers.
           - Maintains a limit on detected consecutive pixels to filter out noise.

        4. Lane Tracking:
            - Once initial lane starting points are found, the algorithm tracks the
              lanes by moving upwards (reducing the y-coordinate) through the image
              from these starting points.
            - It continuously verifies the lane by attempting to add new lane
              elements (middle points of valid lane sections) found in the upwards
              scan direction, for both left and right lanes.
        """
    def __init__(self):
        self.pixel_getter = None

    def setup(self, pixel_getter):
        """Initialize with a pixel getter, this should be run once."""
        self.pixel_getter = pixel_getter

    def recognize_lanes(self, img):
        if not self.pixel_getter:
            raise ValueError("Pixel getter has not been set up. Call setup() first.")

        left_lane, right_lane = self.get_lanes(img)
        return left_lane, right_lane

    # ---------------------------------------------------------------
    # Lane recognition

    def set_threshold(self, img):
        """Sets the threshold dynamically based on the image. Dummy function."""
        return

    def get_lane_element(self, img, x, y, from_left=1):
        """
        Finds the lane element in a given row of an image by scanning horizontally
        from a given starting point. It detects the lane by counting consecutive
        pixels below a predefined intensity threshold. If a sufficient number of
        consecutive low-intensity pixels are found, it identifies this as a lane
        element and computes its middle point. If there are to many consecutive
        intensity pixels, it returns None.

        Parameters:
            img: int[][] - A 2D array representing the grayscale image.
            x: int - The initial horizontal position to start scanning.
            y: int - The vertical row to be scanned for the lane element.
            from_left: int - The direction to scan; 1 for left to right, -1 for right to left.

        Returns:
            tuple[int, int] | None: The (y, x) coordinates of the lane element's
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
            if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                consecutive_count += 1
                if consecutive_count >= CONSECUTIVE_PIXELS:
                    if not first_x:
                        first_x = x
            else:
                consecutive_count = 0

        if consecutive_count < MAX_CONSECUTIVE_PIXELS and first_x is not None:
            # Calculate the middle point of the element
            element = (y, (2 * first_x + consecutive_count) // 2)
        return element

    def get_lane_start(self, img):
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
                element = self.get_lane_element(img, x, y, -1)
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
                element = self.get_lane_element(img, x, y, 1)  # Change scan direction
                if element:
                    right_lane_start = element
                    break
            if right_lane_start: break

        return left_lane_start, right_lane_start

    def get_lanes(self, img):
        """
        Extracts the lanes of lanes from an image by finding sequential elements
        in each lane starting from the initial positions returned by get_lane_start.
        Traverses in an upward direction along the image, alternating between
        adding elements to the left and right lane lists.

        Parameters:
            img: The image data from which lane lanes are to be determined.

        Returns:
            A tuple containing two lists. The first list is the left lane,
            and the second list is the right lane. Each list contains tuples
            of coordinates (y, x) representing the lanes of the lanes.
        """
        left_lane = []
        right_lane = []

        left_start, right_start = self.get_lane_start(img)

        if left_start is not None:
            x = left_start[1]
            for y in range(left_start[0], 20, -10):
                element = self.get_lane_element(img, x, y, -1)
                if not element:
                    break
                x = element[1]
                left_lane.append((y, x))

        if right_start is not None:
            x = right_start[1]
            for y in range(right_start[0], 20, -10):
                element = self.get_lane_element(img, x, y, 1)
                if not element:
                    break
                x = element[1]
                right_lane.append((y, x))

        return left_lane, right_lane