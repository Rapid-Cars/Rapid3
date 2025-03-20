# Constants

CONSECUTIVE_PIXELS = 3 # Number of pixels in a row for it to count as an edge
MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 4 # If the consecutive pixels exceed this value it won't be counted as a lane
THRESHOLD = 85 # Darkness Threshold, can be a constant but can also change dynamically
DIRECTION_CHANGE_THRESHOLD = 50 # How far the border can move in a direction to still count as the other lane
PAST_DIRECTION_CHANGE_SAVING = 10 # For how long past lanes should be saved
COUNT_PAST_DIRECTION_CHANGE = 0
CHECK_HEIGHT = 120 # 0-239 0: Top of image 239: Bottom
MAX_ITERATIONS = 8
HEIGHT = 240
WIDTH = 320


LAST_LEFT_LANE = None
LAST_RIGHT_LANE = None

class CenterLaneFinder:
    """
        The CenterLaneFinder class identifies central lanes in grayscale images using pixel intensity values.

        Key Functions:
        1. Initialization:
           - Begins without parameters and requires a pixel getter setup to retrieve pixel values.

        2. Setup:
           - Configures the class with a pixel getter, which is crucial for image processing.

        3. Lane Recognition:
           - Uses the recognize_lanes method to find potential left and right lane edges
             by scanning a central horizontal line in the image.
           - The find_edge helper method facilitates identification by searching for sequences
             of consecutive low-intensity pixels.

        4. Edge Finding:
           - find_edge scans a horizontal range for consecutive low-intensity pixels,
             marking potential lane edges.
           - Ensures that detected sequences do not exceed a defined maximum to filter out noise.
           - Calculates and returns the coordinates of the midpoint for valid edges.

        5. Constants:
           - Utilizes constants for pixel count thresholds, intensity evaluation,
             and image dimensions (HEIGHT and WIDTH).

        The CenterLaneFinder focuses on detecting lane markings as sequences of low-intensity pixels,
        aiding image processing applications such as autonomous driving and traffic analysis.
        """
    def __init__(self):
        self.pixel_getter = None

    def setup(self, pixel_getter):
        """Initialize with a pixel getter, this should be run once."""
        self.pixel_getter = pixel_getter

    def recognize_lanes(self, img):
        """
        Recognizes lanes from a provided image by identifying the edges of the lanes
        using a pixel getter utility. The method determines the positions of the left
        and right lanes relative to the midpoint of the image.

        Parameters
        ----------
        img : any
            The image from which lanes will be recognized.

        Returns
        -------
        tuple
            A tuple containing two lists: `left_lane` and `right_lane`, each representing
            the detected lane edges as determined by the image analysis.

        Raises
        ------
        ValueError
            If the pixel getter has not been set up prior to executing lane recognition.
        """
        if not self.pixel_getter:
            raise ValueError("Pixel getter has not been set up. Call setup() first.")
        self.set_threshold(img)
        # You can implement another lane recognition algorithm here
        # Get a pixel from the image by using: pixel = self.pixel_getter.get_pixel(img, x, y)
        left_lane, right_lane = [], []
        y = CHECK_HEIGHT #- (HEIGHT // 3) * 2
        iterations = 0
        while not left_lane and not right_lane:
            if not LAST_LEFT_LANE:
                left_start = WIDTH // 2
            else:
                _, x = LAST_LEFT_LANE[0]
                left_start = min(x + DIRECTION_CHANGE_THRESHOLD, WIDTH - 1)
            left = self.find_edge(img, y, left_start, 10)
            if left is not None:
                left_lane.append(left)
            if not LAST_RIGHT_LANE:
                right_start = WIDTH // 2
            else:
                _, x = LAST_RIGHT_LANE[0]
                right_start = max(0, x - DIRECTION_CHANGE_THRESHOLD)
            right = self.find_edge(img, y, right_start, WIDTH - 10)
            if right is not None:
                right_lane.append(right)
            global THRESHOLD
            THRESHOLD = int(THRESHOLD * 1.5)
            iterations += 1
            if THRESHOLD > 200 or iterations > MAX_ITERATIONS:
                break
        left_lane, right_lane = self.check_for_direction_change(left_lane, right_lane)
        return left_lane, right_lane

    def get_threshold(self):
        return THRESHOLD

    def set_threshold(self, img):
        """
        Calculate the average brightness of an image and set a threshold for lane detection.

        This function analyzes the pixel brightness across the image, excluding specified ignore zones,
        to compute the average brightness. The computed value is used as a threshold for lane detection,
        ensuring the process adapts to varying lighting conditions.

        Parameters
        ----------
        img : ndarray
            The input image from which the brightness threshold is calculated.

        Returns
        -------
        int
            The calculated brightness threshold, scaled down to ensure it is suitable for lane detection.
        """
        total_normalized_brightness = 0.0  # Sum of normalized brightness values
        valid_pixel_count = 0  # Count of valid pixels
        lowest_brightness = 255
        for x in range(32, WIDTH - 32, 2):
            # Get pixel brightness (assumed 8-bit value)
            brightness = self.pixel_getter.get_pixel(img, x, CHECK_HEIGHT)
            if brightness < lowest_brightness:
                lowest_brightness = brightness

        global THRESHOLD
        THRESHOLD = int(lowest_brightness * 1.4)
        #print(THRESHOLD)

    def check_for_direction_change(self, left_lane, right_lane):
        """
        Adjusts lane boundaries based on proximity and historical lane data.

        This function checks for potential changes in lane directions by comparing the current positions
        of the left and right lanes with previously recorded positions. If the lanes are within a defined
        threshold, their positions are adjusted or swapped accordingly. Historical lane data is updated
        for future comparisons.

        Parameters
        ----------
        left_lane : list
            A list of coordinates representing the detected left lane. Each element is a tuple (y, x).

        right_lane : list
            A list of coordinates representing the detected right lane. Each element is a tuple (y, x).

        Returns
        ----------
        tuple
            A tuple containing the updated left_lane and right_lane.

        Notes
        ----------
        - The function uses a global variable `DIRECTION_CHANGE_THRESHOLD` to determine proximity.
        - Historical lane data is stored in the global variables `LAST_LEFT_LANE` and `LAST_RIGHT_LANE`.
        - The function maintains a counter `COUNT_PAST_DIRECTION_CHANGE` to manage the saving of empty lanes.
        - The following scenarios are addressed:
            1. If both lanes are close, their coordinates are averaged.
            2. If a lane is close to a previous lane, it is reassigned.
            3. If both lanes are empty for a sustained period, the history is reset.
        """
        global LAST_LEFT_LANE, LAST_RIGHT_LANE

        # Values of both lanes are very similar -> Use average
        if right_lane is not None and left_lane is not None:
            if len(left_lane) > 0 and len(right_lane) > 0:
                y, left_x = left_lane[0]
                _, right_x = right_lane[0]
                if abs(left_x - right_x) < DIRECTION_CHANGE_THRESHOLD:
                    avg = (left_x + right_x) // 2
                    left_lane[0] = [y, avg]
                    right_lane[0] = [y, avg]

        # Check if the left lane exists and there was a right lane previously
        if left_lane is not None and LAST_RIGHT_LANE is not None:
            if len(left_lane) > 0 and len(LAST_RIGHT_LANE) > 0:
                _, left_x = left_lane[0]
                _, last_right_x = LAST_RIGHT_LANE[0]
                if abs(left_x - last_right_x) < DIRECTION_CHANGE_THRESHOLD:
                    # The element of the left lane is within a close distance to the previous right lane
                    # -> Probably still the right lane
                    right_lane = left_lane
                    left_lane = []

        # Check if the right lane exists and there was a left lane previously
        if right_lane is not None and LAST_LEFT_LANE is not None:
            if len(right_lane) > 0 and len(LAST_LEFT_LANE) > 0:
                _, right_x = right_lane[0]
                _, last_left_x = LAST_LEFT_LANE[0]
                if abs(right_x - last_left_x) < DIRECTION_CHANGE_THRESHOLD:
                    # The element of the right lane is within a close distance to the previous left lane
                    # -> Probably still the left lane
                    left_lane = right_lane
                    right_lane = []

        # Check if both lanes are empty and save / discard the saved lanes
        global COUNT_PAST_DIRECTION_CHANGE
        if not left_lane and not right_lane:
            COUNT_PAST_DIRECTION_CHANGE += 1
            if COUNT_PAST_DIRECTION_CHANGE > PAST_DIRECTION_CHANGE_SAVING:
                LAST_LEFT_LANE = left_lane
                LAST_RIGHT_LANE = right_lane
                COUNT_PAST_DIRECTION_CHANGE = 0
        else:
            LAST_LEFT_LANE = left_lane
            LAST_RIGHT_LANE = right_lane
            COUNT_PAST_DIRECTION_CHANGE = 0
        return left_lane, right_lane

    def find_edge(self, img, y, x_start, x_end):
        """
        Finds the first horizontal edge in a specified range of a given image by
        checking for a series of consecutive pixels that are below a defined
        threshold.

        The function scans along a specified horizontal line (`y`) from
        `x_start` to `x_end`, and identifies the first sequence of consecutive
        pixels whose intensity is below a set threshold, indicating a potential
        edge. The position of the edge is calculated as the midpoint of this
        sequence and returned.

        Parameters:
            img: The image to be processed, typically a 2D array or similar
                structure.
            y: int
                The y-coordinate (horizontal line) to scan for edges.
            x_start: int
                The starting x-coordinate of the scan range.
            x_end: int
                The ending x-coordinate of the scan range.

        Returns:
            tuple or None:
                A tuple (y, x) with the y-coordinate of the line and the
                x-coordinate of the detected edge. If no edge is found, returns
                None.
        """
        first_x = None
        consecutive_count = 0
        edge = None
        if x_start < x_end:
            rng = range(x_start, x_end, 1)
        else:
            rng = range(x_start, x_end, -1)
        for x in rng:
            if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                consecutive_count += 1
                if consecutive_count >= CONSECUTIVE_PIXELS:
                    if first_x is None:
                        first_x = x
            else:
                consecutive_count = 0

        if consecutive_count < MAX_CONSECUTIVE_PIXELS and first_x is not None:
            # Calculate the middle point of the element
            edge = (y, (2 * first_x + consecutive_count) // 2)
        return edge