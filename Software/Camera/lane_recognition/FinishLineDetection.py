class FinishLineDetection:
    def __init__(self, pixel_getter, width = 160, height = 120, sobel_threshold = 200,
                 pixel_skip_x = 3, pixel_skip_y = 1, detection_ratio_min = 0.1, detection_ratio_max = 0.25,
                 x_min = 45, x_max = -40, y_min = 75, y_max = 85):
        self.pixel_getter = pixel_getter
        self.width = width # Width of the image
        self.height = height # Height of the image
        self.sobel_threshold = sobel_threshold # Threshold of the sobel function. Min: 0, Max: 1530
        self.pixel_skip_x = pixel_skip_x # The interval of pixels that will be counted (1: Every pixel, 2: Every 2nd pixel, ...)
        self.pixel_skip_y = pixel_skip_y # See above
        # Search area constants
        # x_max and y_max can be negative. If they are negative they will be subtracted from the image width / height
        self.x_min = x_min
        if x_max < 0:
            self.x_max = self.width + x_max
        else:
            self.x_max = x_max
        self.y_min = y_min
        if y_max < 0:
            self.y_max = self.height + y_max
        else:
            self.y_max = y_max
        if self.x_max <= self.x_min or self.x_min < 0 or self.x_max > self.width:
            raise ValueError("The value(s) for x_min and / or x_max are not correct")
        if self.y_max <= self.y_min or self.y_min < 0 or self.y_max > self.height:
            raise ValueError("The value(s) for y_min and / or y_max are not correct")

        self.detection_count_min = (self.x_max - self.x_min) * (self.y_max - self.y_min)
        self.detection_count_min = self.detection_count_min / self.pixel_skip_x / self.pixel_skip_y
        self.detection_count_max = round(self.detection_count_min * detection_ratio_max)
        self.detection_count_min = round(self.detection_count_min * detection_ratio_min)

    def check_for_finish_line(self, img):
        return self.find_blobs(img)
        count = 0

        # Count the number of detected edge pixels
        for y in range(self.y_min, self.y_max, self.pixel_skip_y):
            for x in range(self.x_min, self.x_max, self.pixel_skip_x):
                if self.pixel_getter.get_pixel(img, x, y):
                    count += 1

        # Check if condition is met
        if self.detection_count_min < count < self.detection_count_max: # Precondition met
            return self.find_blobs(img)
        return False

    def find_blobs(self, img, canvas = None):
        """ ToDo:
        If you modify this function to check a bigger y range (e.g from 40 to 90) and then delimit the maximum length
        of blobs the code is pretty good in recognizing lanes.
        """
        visited = set()
        blobs = []


        max_counter = 500

        def bfs(start_x, start_y):
            queue = [(start_x, start_y)]
            blob_pixels = []
            counter = 0
            while queue:
                counter += 1
                if counter > max_counter: # To many elements in Blob, is not valid
                    return
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
                        min_x = max(1, (start_x - 30))
                        min_y = max(1, (start_y - 10))
                        max_x = min(self.width - 2, (start_x + 30))
                        max_y = min(self.height - 2, (start_y + 10))
                        if min_x <= nx < max_x and min_y <= ny < max_y and (nx, ny) not in visited:
                            if self.pixel_getter.get_pixel(img, nx, ny):
                                queue.append((nx, ny))

            return blob_pixels
        # Iterate over the image to find blobs
        for y in range(self.y_min, self.y_max, self.pixel_skip_y):
            for x in range(self.x_min, self.x_max, self.pixel_skip_x):
                if (x, y) not in visited:
                    if self.pixel_getter.get_pixel(img, x, y):
                        blob = bfs(x, y)
                        if blob:
                            blobs.append(blob)

        # Validate blobs as target markers
        valid_blobs = []
        for blob in blobs:
            if self.blob_is_valid(blob):
                valid_blobs.append(blob)
        if canvas is not None:
            if len(blobs) > 0:
                pass
                #self.visualize_blobs(blobs, canvas)
            if len(valid_blobs) > 0:
                #pass
                self.visualize_blobs(valid_blobs, canvas)
        if len(valid_blobs) > 0:
            if len(valid_blobs) == 2:
                return True # Found two valid blobs, will return True
            # Found one valid blob
            # Check for the next blob in the area left and right of the first one
            for valid_blob in valid_blobs:
                left_blob_start, right_blob_start = self.find_blob_direction(valid_blob)
                if canvas is not None:
                    canvas[left_blob_start[1], left_blob_start[0]] = (255, 128, 64)
                    canvas[right_blob_start[1], right_blob_start[0]] = (64, 128, 255)
                    pass
                blob_left = bfs(left_blob_start[0], left_blob_start[1])
                if blob_left:
                    if self.blob_is_valid(blob_left):
                        if canvas is not None:
                            self.visualize_blobs([blob_left], canvas)
                        print("Finish left")
                        return True
                blob_right = bfs(right_blob_start[0], right_blob_start[1])
                if blob_right:
                    if self.blob_is_valid(blob_right):
                        if canvas is not None:
                            self.visualize_blobs([blob_right], canvas)
                        print("Finish right")
                        return True
        return False

    def blob_is_valid(self, blob):
        marker_min_length = 15 * 15
        marker_max_length = 25 * 25

        x_coords, y_coords = zip(*blob)
        x_min_blob, x_max_blob = min(x_coords), max(x_coords)
        y_min_blob, y_max_blob = min(y_coords), max(y_coords)
        diagonal_length = (x_max_blob - x_min_blob) ** 2 + (y_max_blob - y_min_blob) ** 2

        if marker_min_length <= diagonal_length <= marker_max_length:
            if 4 <= (y_max_blob - y_min_blob) < 15:
                if 12 <= (x_max_blob - x_min_blob) < 30:
                    return True
        return False

    def find_blob_direction(self, blob):
        if not blob:
            return None, None  # Falls der Blob leer ist

            # Extrahiere x- und y-Werte
        x_values = [p[0] for p in blob]
        y_values = [p[1] for p in blob]

        # Berechne die Mittelwerte
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(y_values) / len(y_values)

        # Berechnung der Steigung m (Least Squares Methode)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        m = numerator / denominator if denominator != 0 else 0  # Verhindert Division durch 0

        # Berechnung des y-Achsenabschnitts b
        b = y_mean - m * x_mean

        # Berechnung der Startpunkte für den nächsten Blob entlang der Regressionsgeraden
        interval = 30
        start_x_min = int(x_mean - interval)
        start_y_min = int(m * start_x_min + b)
        start_x_max = int(x_mean + interval)
        start_y_max = int(m * start_x_max + b)

        return (start_x_min, start_y_min), (start_x_max, start_y_max)
        """
        if not blob:
            return None, None  # If blob is empty

        # Get min and max values
        x_min = min(p[0] for p in blob)
        x_max = max(p[0] for p in blob)
        y_min = min(p[1] for p in blob)
        y_max = max(p[1] for p in blob)

        # Calculate the direction of the blob
        y_range = y_max - y_min if y_max - y_min != 0 else 1  # Prevents dividing by zero
        x_dif_per_y = (x_max - x_min) / y_range

        x_range = x_max - x_min if x_max - x_min != 0 else 1 # Prevents dividing by zero
        y_dif_per_x = (y_max - y_min) / x_range

        # Starting points for next blob
        increment = 15
        start_x_min = round(max(1, x_min - increment))
        start_y_min = round(max(1, y_min - increment / 2 * y_dif_per_x))
        start_x_max = round(min(self.width - 2, x_max + increment))
        start_y_max = round(min(self.height - 2, y_max + increment / 2 * y_dif_per_x))

        return (start_x_min, start_y_min), (start_x_max, start_y_max)
        """

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

    def create_binary_image(self, gray_image, canvas):
        #blobs = self.check_precondition(gray_image)

        for y in range(self.y_min, self.y_max, 1):
            canvas[y, self.x_min] = (0, 255, 255)
            canvas[y, self.x_max] = (0, 255, 255)

        for x in range(self.x_min, self.x_max, 1):
            canvas[self.y_min, x] = (0, 255, 255)
            canvas[self.y_max, x] = (0, 255, 255)


        if self.find_blobs(gray_image, canvas):
            pass#print("Finish line detected!")

        #self.visualize_blobs(blobs, canvas)