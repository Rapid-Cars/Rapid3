# Constants
MAX_CONSECUTIVE_PIXELS = 30 # If the consecutive pixels exceed this value it won't be counted as a lane
DIFFERENCE_THRESHOLD = 15 # The difference two pixels have to have in order to be detected as a lane edge
HEIGHT = 240
WIDTH = 320


def remove_duplicates(left_lane, right_lane):
    #ToDo: Same as in BaseInitiated
    if left_lane is None or right_lane is None:
        return left_lane, right_lane
    left_index, right_index = 0, 0

    while left_index < len(left_lane) and right_index < len(right_lane):
        left_y, left_x = left_lane[left_index]
        right_y, right_x = right_lane[right_index]
        if left_y < right_y:
            right_index += 1
        elif left_y > right_y:
            left_index += 1
        else:
            if abs(left_x - right_x) < 20:
                if left_index > right_index:
                    # Remove all elements starting from right_index
                    right_lane = right_lane[:right_index]
                elif left_index < right_index:
                    # Remove all elements starting from left_index
                    left_lane = left_lane[:left_index]
                else:
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
    #ToDO: Create dynamic ignore zone
    y_start = HEIGHT - 55
    y_end = HEIGHT
    x_start = 85
    x_end = WIDTH - 55
    if y_start < y < y_end:
        if x_start < x < x_end:
            return True
    return False


class BaseContrastFinder:
    """

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
    def get_dif(self, first_pixel, second_pixel):
        if first_pixel > second_pixel:
            return first_pixel - second_pixel
        else:
            return second_pixel - first_pixel


    def get_lane_element(self, img, x, y):
        element = None
        x_min = max(x - MAX_CONSECUTIVE_PIXELS - 10, 0)
        x_max = min(x + MAX_CONSECUTIVE_PIXELS + 10, WIDTH - 2)

        i = x_min
        while i <= x_max:
            i += 1
            if get_is_in_ignore_zone(i, y):
                continue
            dif = self.get_dif(self.pixel_getter.get_pixel(img, i-1, y), self.pixel_getter.get_pixel(img, i, y))

            if dif < DIFFERENCE_THRESHOLD:
                continue

            end_range = min(i+MAX_CONSECUTIVE_PIXELS, x_max)
            for j in range(end_range, i+1, -1):
                if get_is_in_ignore_zone(j, y):
                    continue
                dif = self.get_dif(self.pixel_getter.get_pixel(img, j, y), self.pixel_getter.get_pixel(img, j-1, y))
                if dif > DIFFERENCE_THRESHOLD:
                    element = (y, (i-1 + j) // 2)
                    return element

        return element


    def get_lane_start(self, img):
        # Find left lane
        # Search params:
        # x: 10 to (width // 2) - 10
        # y: Start at height - 10 then move to height // 2 TODO
        left_lane_start = None
        for y in range(HEIGHT - 10, 0, -10):
            x = 20
            while x < ((WIDTH // 2) - (2 * MAX_CONSECUTIVE_PIXELS - 10)):
                x += MAX_CONSECUTIVE_PIXELS
                element = self.get_lane_element(img, x, y)
                if element:
                    left_lane_start = element
                    break
            if left_lane_start: break

        # Search params:
        # x: (width // 2) + 10 to width - 10
        # y: Start at height - 10 then move to height // 2 TODO
        right_lane_start = None
        for y in range(HEIGHT - 10, 0, -10):
            x = WIDTH - 20
            while x > ((WIDTH // 2) + (2 * MAX_CONSECUTIVE_PIXELS - 10)):
                x -= MAX_CONSECUTIVE_PIXELS
                element = self.get_lane_element(img, x, y)  # Change scan direction
                if element:
                    right_lane_start = element
                    break
            if right_lane_start: break

        return left_lane_start, right_lane_start

    def get_lanes(self, img):

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

