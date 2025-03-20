# Constants
BLOOM_X = 50
BLOOM_Y = 20
BOTTOM_START = 130
THRESHOLD = 45  # Darkness threshold, can be constant or dynamically adjusted
HEIGHT = 240
WIDTH = 320

class BaseInitMarc:
    """
    ToDo: Describe how your class works here
    """
    def __init__(self):
        self.pixel_getter = None

    def setup(self, pixel_getter):
        """
        Initialize with a pixel getter. This function needs to be run once before lane recognition.
        """
        self.pixel_getter = pixel_getter

    def get_threshold(self):
        return THRESHOLD

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

        # ToDo: Implement lane recognition algorithm here
        # Use this snippet to get a pixel: pixel = self.pixel_getter.get_pixel(img, x, y)

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
        left_lane = []
        right_lane = []
        # img.draw_line(0, BOTTOM_START, 320, BOTTOM_START, color = 255)
        for y in range(BOTTOM_START, BLOOM_Y, -10):
            for x in range(159, 0, -1):
                if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                    # img.draw_line(x, y, 160, y, color = 255)
                    # img.draw_circle(x, y, 10, color=255)
                    left_lane.append((y, x))
                    break
            if left_lane: break

            # Search params:
            # x: (width // 2) + 10 to width - 10
            # y: Start at height - 10 then move to height // 2

        for y in range(BOTTOM_START, BLOOM_Y, -10):
            for x in range(161, 320, 1):
                if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                    # img.draw_line(160, y, x, y, color = 255)
                    # img.draw_circle(x, y, 10, color=255)
                    right_lane.append((y, x))
                    break
            if right_lane: break

        if left_lane:
            self.get_array(left_lane, img)
        if right_lane:
            self.get_array(right_lane, img)

        # print(left_lane, right_lane)
        # img.draw_circle(left_lane[0][0], left_lane[0][0], 15, color = 255)
        # img.draw_circle(right_lane[0][0], right_lane[0][0], 15, color = 255)

        # Start with the last known valid point

        if not left_lane and right_lane:
            left_lane = [[0, 0]]
        if not right_lane and left_lane:
            right_lane = [[0, 0]]
        if not left_lane and not right_lane:
            left_lane = [[0, 0]]
            right_lane = [[0, 0]]

        # print(left_lane, right_lane)

        return left_lane, right_lane

    def get_array(self, arr, img):
        # Start with the last known valid point
        last_x = arr[0][1]  # Initialize from the first point
        direction = 0

        for x in range(max(last_x - BLOOM_X, 0), min(last_x + BLOOM_X, 320), 1):  # Use the last known x value
            if self.pixel_getter.get_pixel(img, x, arr[0][0] - BLOOM_Y) < THRESHOLD:
                #img.draw_circle(x, arr[0][1] - BLOOM_Y, 10, color=255)
                arr.append(((arr[0][0] - BLOOM_Y), x))  # Add the new point to the list
                if x > last_x:
                    direction = 0
                else:
                    direction = 1
                break  # Exit the inner loop once a point is found
            # else:
            # If no pixel is found, decide how to handle this case
            # break
        if direction == 0 and len(arr) > 1:
            for y in range(arr[1][0], 20, -BLOOM_Y):  # Decrement y by BLOOM_Y in each iteration
                for x in range(last_x, min(last_x + BLOOM_X, 320), -1):  # Use the last known x value
                    if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                        #print(img.get_pixel(x, y))
                        #img.draw_circle(x, y, 10, color=255)
                        arr.append((y, x))  # Add the new point to the list
                        last_x = x
                        break
                else:
                    # If no pixel is found, decide how to handle this case
                    break
        elif len(arr) > 1:
            for y in range(arr[1][0] - BLOOM_Y, 20, -BLOOM_Y):  # Decrement y by BLOOM_Y in each iteration
                for x in range(last_x, max(last_x - BLOOM_X, 0), -1):  # Use the last known x value
                    if self.pixel_getter.get_pixel(img, x, y) < THRESHOLD:
                        #img.draw_circle(x, y, 10, color=255)
                        arr.append((y, x))  # Add the new point to the list
                        last_x = x
                        break
                else:
                    # If no pixel is found, decide how to handle this case
                    break