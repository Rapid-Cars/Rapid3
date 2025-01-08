# Constants

CONSECUTIVE_PIXELS = 5 # Number of pixels in a row for it to count as an edge
MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5 # If the consecutive pixels exceed this value it won't be counted as a lane
THRESHOLD = 50 # Darkness Threshold, can be a constant but can also change dynamically
DIRECTION_CHANGE_THRESHOLD = 40
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

        # You can implement another lane recognition algorithm here
        # Get a pixel from the image by using: pixel = self.pixel_getter.get_pixel(img, x, y)
        left_lane, right_lane = [], []
        y = HEIGHT //2 #- (HEIGHT // 3) * 2
        mid_x = WIDTH // 2
        left = self.find_edge(img, y, 10, mid_x)
        if left is not None:
            left_lane.append(left)
        right = self.find_edge(img, y, WIDTH-10, mid_x)
        if right is not None:
            right_lane.append(right)

        left_lane, right_lane = self.check_for_direction_change(left_lane, right_lane)

        return left_lane, right_lane

    def check_for_direction_change(self, left_lane, right_lane):
        #ToDo: Add documentation
        global LAST_LEFT_LANE, LAST_RIGHT_LANE

        if right_lane is not None and left_lane is not None:
            if len(left_lane) > 0 and len(right_lane) > 0:
                y, left_x = left_lane[0]
                _, right_x = right_lane[0]
                if abs(left_x - right_x) < DIRECTION_CHANGE_THRESHOLD:
                    # Values of both lanes are very similar -> Ignore one element
                    avg = (left_x + right_x) // 2
                    left_lane[0] = [y, avg]
                    right_lane[0] = [y, avg]

        if left_lane is not None and LAST_RIGHT_LANE is not None:
            if len(left_lane) > 0 and len(LAST_RIGHT_LANE) > 0:
                # The left lane exists and previously there was a right lane
                _, left_x = left_lane[0]
                _, last_right_x = LAST_RIGHT_LANE[0]
                if abs(left_x - last_right_x) < DIRECTION_CHANGE_THRESHOLD:
                    # The element of the left lane is within a close distance to the previous right lane
                    # -> Probably still the right lane
                    right_lane = left_lane
                    left_lane = []

        if right_lane is not None and LAST_LEFT_LANE is not None:
            if len(right_lane) > 0 and len(LAST_LEFT_LANE) > 0:
                # The right lane exists and previously there was a left lane
                _, right_x = right_lane[0]
                _, last_left_x = LAST_LEFT_LANE[0]
                if abs(right_x - last_left_x) < DIRECTION_CHANGE_THRESHOLD:
                    # The element of the right lane is within a close distance to the previous left lane
                    # -> Probably still the left lane
                    left_lane = right_lane
                    right_lane = []

        LAST_LEFT_LANE = left_lane
        LAST_RIGHT_LANE = right_lane
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
                    if not first_x:
                        first_x = x
            else:
                consecutive_count = 0

        if consecutive_count < MAX_CONSECUTIVE_PIXELS and first_x is not None:
            # Calculate the middle point of the element
            edge = (y, (2 * first_x + consecutive_count) // 2)
        return edge