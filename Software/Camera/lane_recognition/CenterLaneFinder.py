# Constants
CONSECUTIVE_PIXELS = 5 # Number of pixels in a row for it to count as an edge
MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5 # If the consecutive pixels exceed this value it won't be counted as a lane
THRESHOLD = 60 # Darkness Threshold, can be a constant but can also change dynamically
HEIGHT = 240
WIDTH = 320

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
        y = HEIGHT // 2 #- (HEIGHT // 3) * 2
        mid_x = WIDTH // 2
        left = self.find_edge(img, y, 10, mid_x-20)
        if left is not None:
            left_lane.append(left)
        right = self.find_edge(img, y, WIDTH-10, mid_x+20)
        if right is not None:
            right_lane.append(right)

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