# CONSTANTS
HEIGHT = 120
WIDTH = 160
SOBEL_THRESHOLD = 150  # Min: 0 Max: 1530
PAST_DIRECTION_CHANGE_SAVING = 1  # For how many frames past lanes should be saved
DIRECTION_CHANGE_THRESHOLD = 25  # 50  # How far one lane can move per frame without being counted as the other lane
PREDICTION_MARGIN = 10  # 20  # Allowed deviation for the predicted x-range
# CHECK_HEIGHTS = [50, 100, 130]  # 0-239 0: Top of image 239: Bottom Important: Increase the values from left to right
CHECK_HEIGHTS = [45, 60, 70, 80, 85]  # For QQVGA
L1_L2_MIN = 55  # 90 #minimal difference for the x - Values in CHECK_HEIGHTS[1] & CHECK_HEIGHTS_[2] to be seperated as 2 different lanes
# GLOBAL VARIABLES
COUNT_PAST_DIRECTION_CHANGE = None
LAST_LEFT_LANE = None
LAST_RIGHT_LANE = None
LEFT_CHANGE = None
RIGHT_CHANGE = None


def set_element_at_height(y, a_tuple, element):
    """
    Sets the y value of a given tuple to element.
    If the tuple does not exist or the y-element is not in the tuple,
    the tuple will be created.
    """
    if a_tuple is None:
        a_tuple = []

    # Remove the existing (y, element) if it exists
    a_tuple = [(h, v) for h, v in a_tuple if h != y]

    if element is not None:
        a_tuple.append((y, element))

    return a_tuple


def get_element_at_height(y, a_tuple):
    """
    Returns the element of a given tuple at the height y.
    """
    if a_tuple is not None:
        if len(a_tuple) > 0:
            for last_y, element in a_tuple:
                if last_y == y:
                    return element


def adjust_lanes(left_lane, right_lane, height_bottom, height_mid):
    """
    Adjusts lane positions by moving elements from one lane to another based on height and proximity conditions.

    Parameters:
        left_lane (list): List of tuples representing (y, x) positions in the left lane.
        right_lane (list): List of tuples representing (y, x) positions in the right lane.
        height_bottom (int): The lower height value to check.
        height_mid (int): The middle height value to check.

    Returns:
        tuple: Updated left_lane and right_lane lists.
    """
    left_bottom = get_element_at_height(height_bottom, left_lane)
    right_bottom = get_element_at_height(height_bottom, right_lane)

    left_mid = get_element_at_height(height_mid, left_lane)
    right_mid = get_element_at_height(height_mid, right_lane)

    # Check if the element at height_bottom in left_lane and height_mid in right_lane are close
    if (
            left_bottom is not None
            and right_mid is not None
            and abs(left_bottom - right_mid) <= L1_L2_MIN
    ):
        if left_mid is None:
            # Move the element at height_mid from right_lane to left_lane
            left_lane.append((height_mid, right_mid))
            right_lane = set_element_at_height(height_mid, right_lane, None)

    # Check if the element at height_bottom in right_lane and height_mid in left_lane are close
    if (
            right_bottom is not None
            and left_mid is not None
            and abs(right_bottom - left_mid) <= L1_L2_MIN

    ):
        if right_mid is None:
            # Move the element at height_mid from left_lane to right_lane
            right_lane.append((height_mid, left_mid))
            left_lane = set_element_at_height(height_mid, left_lane, None)

    """
    # Check if the element of a lane is in the expected position. If the difference is to big: Remove that element
    last_y, last_x = None, None
    x_dif_per_y = None
    for y, x in reversed(left_lane):
        if x_dif_per_y is not None:
            new_x_dif_per_y = (x - last_x) / abs(y - last_y)
            if x_dif_per_y == 0:
                continue
            fraction = new_x_dif_per_y / x_dif_per_y
            if fraction > 3 or fraction < 0.3: # Remove element
                left_lane = set_element_at_height(y, left_lane, None)

        if last_y is not None and last_x is not None:
            x_dif_per_y = (x - last_x) / abs(y - last_y)
        last_y, last_x = y, x

    last_y, last_x = None, None
    x_dif_per_y = None
    for y, x in reversed(right_lane):
        if x_dif_per_y is not None:
            new_x_dif_per_y = (x - last_x) / abs(y - last_y)
            if x_dif_per_y == 0:
                continue
            fraction = new_x_dif_per_y / x_dif_per_y
            if fraction > 3 or fraction < 0.3:  # Remove element
                right_lane = set_element_at_height(y, left_lane, None)

        if last_y is not None and last_x is not None:
            x_dif_per_y = (x - last_x) / abs(y - last_y)
        last_y, last_x = y, x
    """
    return left_lane, right_lane


class SobelEdgeDetection:
    """
    This class implements the Sobel edge detection algorithm to detect lane markings.
    The lanes are detected at the heights in CHECK_HEIGHTS.
    """

    def __init__(self):
        self.pixel_getter = None
        global COUNT_PAST_DIRECTION_CHANGE
        for y in CHECK_HEIGHTS:
            COUNT_PAST_DIRECTION_CHANGE = set_element_at_height(y, COUNT_PAST_DIRECTION_CHANGE, 0)

    def setup(self, pixel_getter):
        """
        Initialize with a pixel getter. This function needs to be run once before lane recognition.
        """
        self.pixel_getter = pixel_getter

    def sobel_operator(self, img, x, y):
        """
        Applies the Sobel operator to calculate the gradient magnitude at a given pixel.
        """
        momo = int(self.pixel_getter.get_pixel(img, x - 1, y - 1))  # MinusOneMinusOne
        pomo = int(self.pixel_getter.get_pixel(img, x + 1, y - 1))  # PlusOneMinusOne
        mopo = int(self.pixel_getter.get_pixel(img, x - 1, y + 1))  # MinusOnePlusOne
        popo = int(self.pixel_getter.get_pixel(img, x + 1, y + 1))  # PlusOnePlusOne

        Gx = (
                -1 * (momo + 2 * int(self.pixel_getter.get_pixel(img, x - 1, y)) + mopo) +
                pomo + 2 * int(self.pixel_getter.get_pixel(img, x + 1, y)) + popo
        )

        Gy = (
                -1 * (momo + 2 * int(self.pixel_getter.get_pixel(img, x, y - 1)) + pomo) +
                mopo + 2 * int(self.pixel_getter.get_pixel(img, x, y + 1)) + popo
        )
        return abs(Gx) + abs(Gy)

    def recognize_lanes(self, img):
        """
        Recognizes the left and right lane positions at predefined heights in the image.

        Parameters:
            img (numpy.ndarray): The input image containing the lane markings.

        Returns:
            tuple: Two lists containing the detected (y, x) coordinates for the left and right lanes.
        """
        left_lane, right_lane = [], []
        for y in CHECK_HEIGHTS:
            left_x, right_x = self.find_lane_at_height(img, y)
            if left_x:
                left_lane.append((y, left_x))
            if right_x:
                right_lane.append((y, right_x))

        for i in range(len(CHECK_HEIGHTS) - 1, 0, -1):
            if (CHECK_HEIGHTS[i] - CHECK_HEIGHTS[i - 1]) <= 20:
                left_lane, right_lane = adjust_lanes(left_lane, right_lane, CHECK_HEIGHTS[i], CHECK_HEIGHTS[i-1])
            else:
                """
                y-difference is to big -> No certainty that the next element is correct
                Stopping the function
                """
                break
        global LAST_LEFT_LANE, LAST_RIGHT_LANE
        LAST_LEFT_LANE = left_lane
        LAST_RIGHT_LANE = right_lane
        return left_lane, right_lane

    def find_lane_at_height(self, img, y):
        """
        Detects the lane positions at a specific height in the image.

        Parameters:
            img (numpy.ndarray): The input image containing the lane markings.
            y (int): The vertical position in the image where lane detection is performed.

        Returns:
            tuple: The x-coordinates of the left and right lanes at the given height.
                   Returns (None, None) if no lanes are detected.
        """
        global LEFT_CHANGE, RIGHT_CHANGE, LAST_LEFT_LANE, LAST_RIGHT_LANE
        # Find left element
        last_left_x = get_element_at_height(y, LAST_LEFT_LANE)
        if last_left_x is not None:
            left_x_change = get_element_at_height(y, LEFT_CHANGE)
            left_x = self.find_lane_element(img, y, last_x=last_left_x, x_change=left_x_change, direction=-1)
            if left_x is not None:
                left_x_change = left_x - last_left_x
                LEFT_CHANGE = set_element_at_height(y, LEFT_CHANGE, left_x_change)
        else:
            left_x = self.find_lane_element(img, y, direction=-1, start_x=WIDTH // 2, end_x=1)
            LEFT_CHANGE = set_element_at_height(y, LEFT_CHANGE, 0)

        # Find right element
        last_right_x = get_element_at_height(y, LAST_RIGHT_LANE)
        if last_right_x is not None:
            right_x_change = get_element_at_height(y, RIGHT_CHANGE)
            right_x = self.find_lane_element(img, y, last_x=last_right_x, x_change=right_x_change, direction=1)
            if right_x is not None:
                right_x_change = right_x - last_right_x
                RIGHT_CHANGE = set_element_at_height(y, RIGHT_CHANGE, right_x_change)
        else:
            right_x = self.find_lane_element(img, y, direction=1, start_x=WIDTH // 2, end_x=WIDTH - 3)
            RIGHT_CHANGE = set_element_at_height(y, RIGHT_CHANGE, 0)

        # Check if left_x was found and there was a right lane previously
        if left_x is not None and last_right_x is not None:
            if abs(left_x - last_right_x) < DIRECTION_CHANGE_THRESHOLD:
                # The element of the left lane is within a close distance to the previous right lane
                # -> Probably still the right lane
                right_x = left_x
                left_x = None

        # Check if right_x was found and there was a left lane previously
        if right_x is not None and last_left_x is not None:
            if abs(right_x - last_left_x) < DIRECTION_CHANGE_THRESHOLD:
                # The element of the right lane is within a close distance to the previous left lane
                # -> Probably still the left lane
                left_x = right_x
                right_x = None

        # Check if both lanes exist
        if left_x is not None and right_x is not None:
            if left_x > right_x:  # Left lane is right of right lane
                if last_left_x is None:  # No left lane previously
                    left_x = None
                if last_right_x is None:  # No right lane previously
                    right_x = None
            elif abs(right_x - left_x) < DIRECTION_CHANGE_THRESHOLD:  # Values of both lanes are similar. Delete one lane
                if last_left_x is None: left_x = None
                if last_right_x is None: right_x = None

        # Check if both lanes are empty and save / discard lanes
        global COUNT_PAST_DIRECTION_CHANGE
        if left_x is None and right_x is None:
            cpdr = get_element_at_height(y, COUNT_PAST_DIRECTION_CHANGE)
            COUNT_PAST_DIRECTION_CHANGE = set_element_at_height(y, COUNT_PAST_DIRECTION_CHANGE, cpdr + 1)
            if cpdr > PAST_DIRECTION_CHANGE_SAVING:
                LAST_LEFT_LANE = set_element_at_height(y, LAST_LEFT_LANE, None)
                LAST_RIGHT_LANE = set_element_at_height(y, LAST_RIGHT_LANE, None)
                COUNT_PAST_DIRECTION_CHANGE = set_element_at_height(y, COUNT_PAST_DIRECTION_CHANGE, 0)
        else:
            LAST_LEFT_LANE = set_element_at_height(y, LAST_LEFT_LANE, left_x)
            LAST_RIGHT_LANE = set_element_at_height(y, LAST_RIGHT_LANE, right_x)
            COUNT_PAST_DIRECTION_CHANGE = set_element_at_height(y, COUNT_PAST_DIRECTION_CHANGE, 0)
        return left_x, right_x

    def find_lane_element(self, img, y, last_x=None, x_change=0, direction=1, start_x=None, end_x=None):
        """
        Searches for a lane element in the image at a specific height.

        Parameters:
            img (numpy.ndarray): The input image containing the lane markings.
            y (int): The vertical position in the image where the search is performed.
            last_x (int, optional): The previous x-coordinate of the lane element.
            x_change (int, optional): The predicted change in x position from the last frame.
            direction (int, optional): The direction of search (-1 for left, 1 for right). Default is 1.
            start_x (int, optional): The starting x-coordinate for the search.
            end_x (int, optional): The ending x-coordinate for the search.

        Returns:
            int or None: The detected x-coordinate of the lane element, or None if no lane is found.
        """
        # Get start and end x-values
        if last_x is None:
            if start_x is None and end_x is None:  # Check if there are start and end x-values
                return
        else:  # Generate start and end x-values for x if there was a previous x-value
            start_x = min(WIDTH - 3, max(1, last_x + x_change - direction * PREDICTION_MARGIN))
            end_x = min(WIDTH - 3, max(1, last_x + x_change + direction * PREDICTION_MARGIN))

        # Get lane element
        if start_x < end_x:
            rng = range(start_x, end_x, 1)
        else:
            rng = range(start_x, end_x, -1)
        for x in rng:
            if self.pixel_getter.get_pixel(img, x, y):
                return x

    def get_threshold(self):
        return 0

    def create_binary_image(self, img, canvas):
        # Temporary, until virtual_cam.py / make_image_binary is improved to don't use the brightness values
        """
        for y in range(1, HEIGHT -2, 2):
            for x in range(1, WIDTH - 2, 1):
                intensity = self.sobel_operator(img, x, y)
                if intensity > SOBEL_THRESHOLD:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                canvas[y, x] = color
        return
        """
        return
        for check_height in CHECK_HEIGHTS:
            for y in range(check_height - 3, check_height + 3, 1):
                for x in range(1, WIDTH - 2):
                    intensity = self.sobel_operator(img, x, y)
                    if intensity > SOBEL_THRESHOLD:
                        color = (255, 255, 255)
                    else:
                        color = (0, 0, 0)
                    canvas[y, x] = color

        for y in range(1, HEIGHT -2, 1):
            for x in range((WIDTH // 2) - 3, (WIDTH // 2) + 3, 1):
                intensity = self.sobel_operator(img, x, y)
                if intensity > SOBEL_THRESHOLD:
                    color = (255, 255, 255)
                else:
                    color = (0, 0, 0)
                canvas[y, x] = color