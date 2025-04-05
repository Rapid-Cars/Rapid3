# Constants
HEIGHT = 120
WIDTH = 160
SOBEL_THRESHOLD = 200  # Min: 0 Max: 1530
X_DIF_HEIGHT = 5 # Number of lines in between elements used to calculate x_dif

TOP_END = 10 # Where the image should end at the top
BOTTOM_END = HEIGHT - 30 # Where the search should start

NO_LANE_THRESHOLD = 5 # Number of unsuccessful lanes until the search for lines will be stopped
X_SEARCH_RANGE = 10 # A lane element will be searched in this range around the expected

def get_is_in_ignore_zone(x, y):
    """
    Checks whether the given point is in the ignore zone.

    Parameters:
            x: int - The x coordinate to be checked.
            y: int - The y coordinate to be checked.
    """
    y_min = HEIGHT
    y_max = HEIGHT - 30
    x_min = 50
    x_max = WIDTH - 40
    if y_max < y < y_min:
        if x_min < x < x_max:
            return True
    return False


class SobelContinuousLaneFinder:

    def __init__(self):
        self.pixel_getter = None

    def setup(self, pixel_getter):
        """
        Initialize with a pixel getter. This function needs to be run once before lane recognition.
        """
        self.pixel_getter = pixel_getter

    def recognize_lanes(self, img, canvas = None):
        left_lane, right_lane =  [], []

        # Not necessary (maybe)
        left_start, right_start = self.find_first_element(img)
        if left_start:
            left_lane.append((BOTTOM_END, left_start))
        if right_start:
            right_lane.append((TOP_END, right_start))
        # END Not necessary (maybe)


        blobs = self.find_blobs(img, left_start, right_start, canvas)

        """
        ToDo:
        - Get lane elements from the blobs. To do this do the following
          - For specific y values get the appropriate x value of a blob
            - Average: Generally good, weak if there are wrong values in the blob
            - Inner value (for left lane, the biggest and for right lane the smallest) good on straight lines, not so good on curves
            - Average, starting from inner value and only counting those with x_dif < 2. This will filter outliers
          - This should be enough to calculate get the lanes up to an intersection
        - Detect intersections (lack in lane or the lane has a 90 degree angle or both lanes suddenly move outwards)
          - Find the direction in which the lane was pointing
          - Move upwards from there
          - Check if you find a lane start there
            - Store this lane start for the next frame
            - Repeat
            - If the value is low enough (in the picture, so a high y value (e.g. BOTTOM_END): Stop intersection mode
          - Detect blobs again
          - Return intersection mode?
            - Alternative: Fill in the blanks. Extrapolate the lane elements (from bottom to top and top to bottom). Then Guess what the x value should be.
        """

        return left_lane, right_lane

    def find_first_element(self, img):
        """
        Scans the image starting from the bottom. It scans the complete width and stores every element which is
        above the SOBEL_THRESHOLD. In the end it checks if more than to elements are in that list. If so, it does this
        in the lane above as well.
        """
        # Alternative approach: Calculate the lane like it is done in SobelEdgeDetection.
        # This should only be done for one element
        # Alternative 2: Find a good point on a lane that was already detected. Then go from there
        # ToDo: Check if there were lane elements present previously. If not: Check the entire lane
        y = BOTTOM_END
        pixels = []
        for x in range(1, WIDTH - 2):
            if self.pixel_getter.get_pixel(img, x, y):
                pixels.append(x)
        # ToDo: Remove duplicate pixels here
        if len(pixels) > 1: # ToDo: Improve this condition
            # ToDo: Check if it is a left or right lane here
            return pixels[0], pixels[-1]

        return None, None

    def find_blobs(self, img, left_lane_start, right_lane_start, canvas = None):

        visited = set()
        blobs = []

        def bfs(start_x, start_y):
            queue = [(start_x, start_y)]
            blob_pixels = []
            while queue:
                x, y = queue.pop(0)
                if (x, y) in visited:
                    continue

                visited.add((x, y))
                blob_pixels.append((x, y))

                # Search for neighboring pixels (including diagonals)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 1 <= nx < WIDTH - 2 and 30 <= ny < HEIGHT - 2 and (nx, ny) not in visited and not get_is_in_ignore_zone(nx, ny):
                            if self.pixel_getter.get_pixel(img, x, y):
                                queue.append((nx, ny))

            return blob_pixels
        # Iterate over the image to find blobs

        y = BOTTOM_END
        for x in range(1, WIDTH - 2):
            if (x, y) not in visited:
                if self.pixel_getter.get_pixel(img, x, y):
                    blob = bfs(x, y)
                    if blob:
                        blobs.append(blob)

        # ToDo
        """
        a) Check the length of the blobs
        b) If the length is above 2, there are too many blobs. Remove the shortest one (?)
        c) Check which one is the left lane and which one is the right lane
        d) Store one x and y value of the blob (not directly at the border. I would recommend y = HEIGHT - 30
            This should be used to get the starting value for the next frame.
        """


        if canvas is not None:
            if len(blobs) > 0:
                pass#self.visualize_blobs(blobs, canvas)

    def visualize_blobs(self, blobs, canvas):
        if not blobs: return
        if len(blobs) == 0: return
        colors = [(128, 128, 255), (128, 255, 128), (255, 128, 128), (128, 200, 255), (192, 128, 192), (255, 255, 128)]
        color = 0
        for blob in blobs:
            for x,y in blob:
                canvas[y, x] = colors[color]
            color += 1
            if color >= len(colors):
                color = 0

    def get_threshold(self):
        return 0

    def create_binary_image(self, img, canvas):
        # Temporary, until virtual_cam.py / make_image_binary is improved to don't use the brightness values
        self.recognize_lanes(img, canvas)