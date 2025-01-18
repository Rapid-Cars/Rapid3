# Constants
HEIGHT = 240
WIDTH = 320

# region Static functions -----------------------------------------------------------------

def remove_duplicates(left_lane, right_lane):
    """
    Remove duplicate lane entries based on proximity and starting positions.

    This function compares the y-coordinates and x-coordinates of elements in the
    left and right lane lists to identify and remove duplicates. If two entries have
    very close x-coordinates and identical y-coordinates, they are considered duplicates.
    The function also considers which lane starts further down to decide which list to truncate.

    Parameters
    ----------
    left_lane : list of tuple
        A list of tuples representing the coordinates of the left lane boundary.

    right_lane : list of tuple
        A list of tuples representing the coordinates of the right lane boundary.

    Returns
    -------
    tuple
        A tuple containing the modified left_lane and right_lane lists with duplicates removed.
    """
    if left_lane is None or right_lane is None:
        return left_lane, right_lane
    left_index, right_index = 0, 0

    first_left_y, first_right_y = 0, 0

    if left_lane:
        first_left_y = left_lane[left_index]
    if right_lane:
        first_right_y = right_lane[right_index]

    while left_index < len(left_lane) and right_index < len(right_lane):
        left_y, left_x = left_lane[left_index]
        right_y, right_x = right_lane[right_index]
        if left_y < right_y:
            right_index += 1
        elif left_y > right_y:
            left_index += 1
        else:
            if abs(left_x - right_x) < 20: # Difference between elements is very small -> Duplicate lane
                if first_left_y > first_right_y: # Left lane start further down -> Remove right lane
                    # Remove all elements starting from right_index
                    right_lane = right_lane[:right_index]
                elif first_left_y < first_right_y: # Right lane starts further down -> Remove left lane
                    # Remove all elements starting from left_index
                    left_lane = left_lane[:left_index]
                else: # Lanes have the same start -> Remove both
                    # Remove all elements starting from both indices
                    left_lane = left_lane[:left_index]
                    right_lane = right_lane[:right_index]
                # Exit the loop after truncation to avoid further processing
                break
            else:
                left_index += 1
                right_index += 1

    return left_lane, right_lane


def get_is_in_ignore_zone(x, y):
    """
    Checks whether the given point is in the ignore zone.

    Parameters:
            x: int - The x coordinate to be checked.
            y: int - The y coordinate to be checked.
    """
    y_min = HEIGHT
    y_max = HEIGHT - 50  # For position 3
    x_min = 70
    x_max = WIDTH - 70
    if y_max < y < y_min:
        if x_min < x < x_max:
            return True
    return False

# endregion

# region Super Class BaseInitiatedFinder --------------------------------------------------

class BaseInitiatedFinder:
    MAX_CONSECUTIVE_PIXELS = None  # To be overridden by subclasses

    # region setup

    def __init__(self):
        self.pixel_getter = None


    def setup(self, pixel_getter):
        self.pixel_getter = pixel_getter


    def recognize_lanes(self, img):
        if not self.pixel_getter:
            raise ValueError("Pixel getter has not been set up. Call setup() first.")
        return self.get_lanes(img)

    # endregion

    def get_lane_element(self, img, x, y):
        raise NotImplementedError("Subclasses must implement get_lane_element method.")

    # region Shared functions

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
        # y: Start at height - 10 then move to 0
        left_lane_start = None
        for y in range(HEIGHT - 10, 0, -10):
            x = 20
            while x < ((WIDTH // 2) - (2 * self.MAX_CONSECUTIVE_PIXELS - 10)):
                x += self.MAX_CONSECUTIVE_PIXELS
                element = self.get_lane_element(img, x, y)
                if element:
                    left_lane_start = element
                    break
            if left_lane_start: break

        # Search params:
        # x: (width // 2) + 10 to width - 10
        # y: Start at height - 10 then move to 0
        right_lane_start = None
        for y in range(HEIGHT - 10, 0, -10):
            x = WIDTH - 20
            while x > ((WIDTH // 2) + (2 * self.MAX_CONSECUTIVE_PIXELS - 10)):
                x -= self.MAX_CONSECUTIVE_PIXELS
                element = self.get_lane_element(img, x, y)  # Change scan direction
                if element:
                    right_lane_start = element
                    break
            if right_lane_start: break

        return left_lane_start, right_lane_start


    def get_lanes(self, img):
        """
        Detect and extract left and right lane boundaries from an image.

        This function identifies the starting points of the left and right lanes and then iteratively
        traces the lane boundaries by extracting lane elements at regular intervals. The identified
        lanes are returned after removing duplicates to ensure accuracy.

        Parameters
        ----------
        img : ndarray
            The input image from which lane boundaries need to be detected. The image should
            be pre-processed to enhance lane visibility if required.

        Returns
        -------
        tuple
            A tuple containing two lists:
            - left_lane: List of tuples representing the (y, x) coordinates of the left lane boundary.
            - right_lane: List of tuples representing the (y, x) coordinates of the right lane boundary.
        """
        left_lane = []
        right_lane = []

        left_start, right_start = self.get_lane_start(img)

        if left_start is not None:
            x = left_start[1]
            for y in range(left_start[0], 20, -10):
                element = self.get_lane_element(img, x, y)
                if not element:
                    continue
                x = element[1]
                left_lane.append((y, x))

        if right_start is not None:
            x = right_start[1]
            for y in range(right_start[0], 20, -10):
                element = self.get_lane_element(img, x, y)
                if not element:
                    continue
                x = element[1]
                right_lane.append((y, x))

        return remove_duplicates(left_lane, right_lane)

    # endregion

# endregion

# region BaseInitiatedContrastFinder ------------------------------------------------------

class BaseInitiatedContrastFinder(BaseInitiatedFinder):
    MAX_CONSECUTIVE_PIXELS = 30  # If the consecutive pixels exceed this value it won't be counted as a lane
    DIFFERENCE_THRESHOLD = 15  # The difference two pixels have to have in order to be detected as a lane edge


    def get_dif(self, first_pixel, second_pixel):
        """
        Calculate the difference in brightness between two pixels.
        """
        if first_pixel > second_pixel:
            return first_pixel - second_pixel
        else:
            return second_pixel - first_pixel


    def get_lane_element(self, img, x, y):
        """
        Identify a lane element at a specific position in the image.

        This function scans a horizontal range around the given x-coordinate at a specific y-coordinate
        in the image to detect a significant difference in pixel intensity (contrast). When such a difference is
        found, it determines the midpoint of the detected range as the lane element's position.

        Parameters
        ----------
        img : ndarray
            The input image in which the lane element needs to be detected.

        x : int
            The x-coordinate around which the search for the lane element begins.

        y : int
            The y-coordinate at which the search for the lane element is performed.

        Returns
        -------
        tuple or None
            A tuple (y, x) representing the detected lane element's position, or None if no element is found.
        """
        element = None
        x_min = max(x - self.MAX_CONSECUTIVE_PIXELS - 10, 0)
        x_max = min(x + self.MAX_CONSECUTIVE_PIXELS + 10, WIDTH - 2)

        i = x_min
        while i <= x_max:
            i += 1
            if get_is_in_ignore_zone(i, y):
                continue
            dif = self.get_dif(self.pixel_getter.get_pixel(img, i-1, y), self.pixel_getter.get_pixel(img, i, y))

            if dif < self.DIFFERENCE_THRESHOLD:
                continue

            end_range = min(i + self.MAX_CONSECUTIVE_PIXELS, x_max)
            for j in range(end_range, i+1, -1):
                if get_is_in_ignore_zone(j, y):
                    continue
                dif = self.get_dif(self.pixel_getter.get_pixel(img, j, y), self.pixel_getter.get_pixel(img, j-1, y))
                if dif > self.DIFFERENCE_THRESHOLD:
                    element = (y, (i-1 + j) // 2)
                    return element

        return element

# endregion

# region BaseInitiatedDarknessFinder ------------------------------------------------------

class BaseInitiatedDarknessFinder(BaseInitiatedFinder):
    CONSECUTIVE_PIXELS = 4  # Number of pixels in a row for it to count as an edge
    MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5  # If the consecutive pixels exceed this value it won't be counted as a lane
    THRESHOLD = 50  # Darkness Threshold, can be a constant but can also change dynamically


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

        for y in range(24, HEIGHT - 24, 10):
            for x in range(32, WIDTH - 32, 10):
                if not get_is_in_ignore_zone(x, y):
                    # Get pixel brightness (assumed 8-bit value)
                    brightness = self.pixel_getter.get_pixel(img, x, y)

                    # Normalize brightness to a 0-1 range
                    normalized_brightness = brightness / 255.0

                    # Accumulate normalized brightness
                    total_normalized_brightness += normalized_brightness
                    valid_pixel_count += 1

        # Avoid division by zero if no valid pixels
        if valid_pixel_count == 0:
            return 0

        # Compute average normalized brightness
        average_normalized_brightness = total_normalized_brightness / valid_pixel_count

        # Scale back to 0-255 range
        average_brightness = average_normalized_brightness * 255

        return int(average_brightness / 2)


    def get_lane_element(self, img, x, y):
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

        Returns:
            tuple[int, int] | None: The (y, x) coordinates of the lane element's
            middle point if found, otherwise None.
        """
        element = None
        consecutive_count = 0
        first_x = None
        x_min = max(x - self.MAX_CONSECUTIVE_PIXELS - 10, 0)
        x_max = min(x + self.MAX_CONSECUTIVE_PIXELS + 10, WIDTH - 1)
        if x_max < x_min:
            rng = range(x_max, x_min, -1)
        else:
            rng = range(x_min, x_max, 1)
        for x in rng:
            if get_is_in_ignore_zone(x, y):
                continue
            if self.pixel_getter.get_pixel(img, x, y) < self.THRESHOLD:
                consecutive_count += 1
                if consecutive_count >= self.CONSECUTIVE_PIXELS:
                    if not first_x:
                        first_x = x
            else:
                consecutive_count = 0

        if consecutive_count < self.MAX_CONSECUTIVE_PIXELS and first_x is not None:
            # Calculate the middle point of the element
            element = (y, (2 * first_x + consecutive_count) // 2)
        return element

# endregion