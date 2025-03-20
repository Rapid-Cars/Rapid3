HEIGHT = 240
WIDTH = 320
THRESHOLD = 250 # Min: 0 Max: 1530
CHECK_HEIGHT = 120 # 0-239 0: Top of image 239: Bottom
PAST_DIRECTION_CHANGE_SAVING = 10 # For how long past lanes should be saved
DIRECTION_CHANGE_THRESHOLD = 50 # How far the border can move in a direction to still count as the other lane

LAST_LEFT_LANE = None
LAST_RIGHT_LANE = None

class SobelEdgeDetection:
    """
    This class implements the Sobel edge detection algorithm to detect the lanes
    """
    def __init__(self):
        self.pixel_getter = None

    def setup(self, pixel_getter):
        """
            Initialize with a pixel getter. This function needs to be run once before lane recognition.
        """
        self.pixel_getter = pixel_getter

    def sobel_operator(self, img, x, y):
        """
        Applies the Sobel operator to calculate the gradient magnitude at a given pixel.
        """
        momo = int(self.pixel_getter.get_pixel(img, x - 1, y - 1)) # MinusOneMinusOne
        pomo = int(self.pixel_getter.get_pixel(img, x + 1, y - 1)) # PlusOneMinusOne
        mopo = int(self.pixel_getter.get_pixel(img, x - 1, y + 1)) # MinusOnePlusOne
        popo = int(self.pixel_getter.get_pixel(img, x + 1, y + 1)) # PlusOnePlusOne

        Gx = (
                -1 * (momo + 2 * int(self.pixel_getter.get_pixel(img, x - 1, y)) + mopo) +
                pomo + 2 * int(self.pixel_getter.get_pixel(img, x + 1, y)) + popo
        )

        Gy = (
                -1 * (momo + 2 * int(self.pixel_getter.get_pixel(img, x, y - 1)) + pomo) +
                mopo + 2 * int(self.pixel_getter.get_pixel(img, x, y + 1)) + popo
        )
        return (abs(Gx) + abs(Gy))

    def recognize_lanes(self, img):
        if not self.pixel_getter:
            raise ValueError("Pixel getter has not been set up. Call setup() first.")

        left_lane, right_lane = [], []

        # Left lane
        if not LAST_LEFT_LANE:
            left_start = WIDTH // 2
        else:
            _, x = LAST_LEFT_LANE[0]
            left_start = min(x + DIRECTION_CHANGE_THRESHOLD, WIDTH - 2)
        left = self.find_edge(img, CHECK_HEIGHT, left_start, 10)
        if left is not None:
            left_lane.append(left)

        # Right lane
        if not LAST_RIGHT_LANE:
            right_start = WIDTH // 2
        else:
            _, x = LAST_RIGHT_LANE[0]
            right_start = max(1, x - DIRECTION_CHANGE_THRESHOLD)
        right = self.find_edge(img, CHECK_HEIGHT, right_start, WIDTH - 10)
        if right is not None:
            right_lane.append(right)

        left_lane, right_lane = self.check_for_direction_change(left_lane, right_lane)
        return left_lane, right_lane


    def find_edge(self, img, y, x_start, x_end):
        if x_start < x_end:
            rng = range(x_start, x_end, 1)
        else:
            rng = range(x_start, x_end, -1)
        for x in rng:
            if self.sobel_operator(img, x, y) > THRESHOLD:
                return (y, x)

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

    def get_threshold(self):
        return 0

    def create_binary_image(self, img, canvas):
        for x in range(0 + 1, WIDTH - 2):
            for y in range(CHECK_HEIGHT - 5, CHECK_HEIGHT + 5):
                intensity = self.sobel_operator(img, x, y)
                if intensity > THRESHOLD:
                    color = (255, 255, 255)
                else:
                    color = (0, 0, 0)
                canvas[y, x] = color


