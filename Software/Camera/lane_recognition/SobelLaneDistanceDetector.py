HEIGHT = 120
WIDTH = 160
SOBEL_THRESHOLD = 200  # Min: 0 Max: 1530
TOP_END = 10 # Where the image should end at the top
BOTTOM_END = HEIGHT - 10  # Where the search should start

class SobelLaneDistanceDetector:
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
        x1 = 48
        x2 = 120
        for y in range(BOTTOM_END, TOP_END, -1):
            y1, y2 = None, None
            if self.pixel_getter.get_pixel(img, x1, y):
                y1 = y

            if self.pixel_getter.get_pixel(img, x2, y):
                y2 = y

            if y1 is not None and y2 is not None:
                if y1 < y2 - 40:
                    return y1

                elif y2 < y1 - 40:
                    return y2

                else:
                    y = (y1 + y2) // 2
                return y

            if y1 is not None:
                return y1

            if y2 is not None:
                return y2

        return 0

    def get_threshold(self):
        return 0

    def create_binary_image(self, img, canvas):
        # Temporary, until virtual_cam.py / make_image_binary is improved to don't use the brightness values
        return
        for y in range(1, HEIGHT -2, 2):
            for x in range(1, WIDTH - 2, 1):
                intensity = self.sobel_operator(img, x, y)
                if intensity > SOBEL_THRESHOLD:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                canvas[y, x] = color
        return
        for check_height in CHECK_HEIGHTS:
            for y in range(check_height - 5, check_height + 5, 1):
                for x in range(1, WIDTH - 2):
                    intensity = self.sobel_operator(img, x, y)
                    if intensity > SOBEL_THRESHOLD:
                        color = (255, 255, 255)
                    else:
                        color = (0, 0, 0)
                    canvas[y, x] = color