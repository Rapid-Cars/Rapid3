import math

HEIGHT = 120
WIDTH = 160

# CHECK_HEIGHTS = [35, 50, 60, 75, 81]  # For QQVGA
CHECK_HEIGHTS = [60, 70, 80, 85]  # For QQVGA
CROSSING_DETECTED = False


def calculate_deviation(left_border_element, right_border_element):
    """
    Calculate the deviation from the center position within a specified width.

    This function computes how far a point, defined by its left and right borders,
    is deviated from the central position within the given width. It is helpful in
    determining how centered a position is relative to its boundaries. The deviation
    is calculated as a proportion of the width.

    Parameters:
    left_border_element: int
        The coordinate of the left border of the position. It should be a non-negative
        integer that does not exceed width.
    right_border_element: int
        The coordinate of the right border of the position. It should be a non-negative
        integer that does not exceed width and should be greater than or equal to
        the left border.

    Returns:
    float
        The deviation from the center as a value between -1 and 1. A negative value
        indicates left deviation, zero indicates center alignment, and a positive
        value indicates right deviation.
    """
    deviation = ((WIDTH // 2) - ((left_border_element + right_border_element) / 2)) / (WIDTH // 2)
    if deviation > 1:
        deviation = 1
    elif deviation < -1:
        deviation = -1
    return deviation


def adjust_deviation(deviation, thresholds):
    """Adjusts the deviation based on given steps"""

    abs_deviation = abs(deviation)
    adjusted_deviation = 1.0  # Standardwert für große Abweichungen

    for threshold, value in thresholds:
        if abs_deviation < threshold:
            adjusted_deviation = value
            break

    return adjusted_deviation * (-1 if deviation < 0 else 1)


def find_closest_in_range(lane, target, range_min, range_max):
    """

    """
    closest_point = None
    closest_distance = float('inf')

    for y, x in lane:
        if range_min <= y <= range_max:
            distance = abs(y - target)
            if distance < closest_distance:
                closest_distance = distance
                closest_point = (y, x)

    return closest_point


def find_deviation_at_height(left_lane, right_lane, check_height):
    # Tolerance for values
    # tolerance = 30
    tolerance = 5
    range_min = check_height - tolerance
    range_max = check_height + tolerance

    # Finds the closest point to the check_height
    closest_left = find_closest_in_range(left_lane, check_height, range_min, range_max)
    closest_right = find_closest_in_range(right_lane, check_height, range_min, range_max)

    # Case 1: Both values exist and the y-values are equal
    if closest_left and closest_right:
        y_left, x_left = closest_left
        y_right, x_right = closest_right
        if y_left == y_right:
            return calculate_deviation(x_left, x_right)

        # Case 2: Both values exist and the y-values are not equal
        # -> Use the value that is closer to the check_height
        left_distance = abs(y_left - check_height)
        right_distance = abs(y_right - check_height)

        if left_distance <= right_distance:
            return calculate_deviation(x_left, WIDTH)
        else:
            return calculate_deviation(0, x_right)

    # Case 3: One value exists and is close to the check_height
    if closest_left:
        _, x_left = closest_left
        # return calculate_deviation(x_left, WIDTH + 100)
        return calculate_deviation(x_left, WIDTH + 50)
    elif closest_right:
        _, x_right = closest_right
        # return calculate_deviation(-100, x_right)
        return calculate_deviation(-50, x_right)

    # Case 4: Nothing found
    return None

def interpolate_deviations(deviations):
    """
    Interpolates missing deviation values based on available data.

    :param deviations: List of tuples (y, deviation)
    :param check_heights: List of all possible y values
    :return: List of tuples (y, deviation) including interpolated values
    """
    if len(deviations) < 2:
        return deviations  # Not enough data for interpolation

    # Extract available y and deviation values
    known_y, known_deviations = zip(*sorted(deviations))
    known_y = list(known_y)

    complete_deviations = []
    for y in CHECK_HEIGHTS:
        if y in known_y:
            deviation = dict(deviations)[y]  # Use existing value
        else:
            # Find the closest surrounding points for proper interpolation
            lower_vals = [y_val for y_val in known_y if y_val < y]
            upper_vals = [y_val for y_val in known_y if y_val > y]

            if lower_vals and upper_vals:
                # Perform linear interpolation
                lower = lower_vals[-1]
                upper = upper_vals[0]
                lower_dev = dict(deviations)[lower]
                upper_dev = dict(deviations)[upper]
                deviation = lower_dev + (upper_dev - lower_dev) * ((y - lower) / (upper - lower))
            elif lower_vals:
                # Extrapolate using last two lower values
                if len(lower_vals) > 1:
                    y1, y2 = lower_vals[-2], lower_vals[-1]
                    dev1, dev2 = dict(deviations)[y1], dict(deviations)[y2]
                    slope = (dev2 - dev1) / (y2 - y1)
                    deviation = dev2 + slope * (y - y2)
                else:
                    deviation = dict(deviations)[lower_vals[-1]]
            elif upper_vals:
                # Extrapolate using first two upper values
                if len(upper_vals) > 1:
                    y1, y2 = upper_vals[0], upper_vals[1]
                    dev1, dev2 = dict(deviations)[y1], dict(deviations)[y2]
                    slope = (dev2 - dev1) / (y2 - y1)
                    deviation = dev1 - slope * (y1 - y)
                else:
                    deviation = dict(deviations)[upper_vals[0]]

        complete_deviations.append((y, deviation))

    return complete_deviations


class StraightAwareCenterLaneDriver:
    """
    TODO: Documentation
    """

    def __init__(self, driving_mode):
        self.last_speed = 0
        self.brake_mode = False
        self.brake_mode_count = 0
        self.count = 0
        self.driving_mode = driving_mode
        self.crossing_count = 0

        # Constants
        self.max_frames_brake_mode = 10
        self.speed_threshold = 30

        if driving_mode == 2:  # MODE: FAST
            self.steering_weights = [(30, 0.0), (40, 0.0), (50, 0.0), (60, 0.75), (70, 0.15), (80, 0.1), (90, 0.0), (100, 0.0)]  # How much the deviation at a specific height should weigh # Higher in the picture: Lower number
            self.steering_thresholds = [(0.08, 0.0), (0.22, 0.15), (0.3, 0.35), (0.35, 0.6), (0.4, 0.9)]  # Adjusts the deviations to calculate the steering value
            self.speeds = [99, 90, 82, 68, 54, 40, 33]  # Max speed, medium speed, slow speed
            self.speed_thresholds = [95, 88, 78, 54, 44, 35]  # How big the lane distance has to be to achieve a certain speed
            self.crossing_duration = 3
        elif driving_mode == 1:  # MODE: MEDIUM
            self.steering_weights = [(30, 0.0), (40, 0.0), (50, 0.0), (60, 0.75), (70, 0.15), (80, 0.1), (90, 0.0), (100, 0.0)]  # How much the deviation at a specific height should weigh # Higher in the picture: Lower number
            self.steering_thresholds = [(0.08, 0.0), (0.22, 0.15), (0.3, 0.35), (0.35, 0.6), (0.4, 0.9)]  # Adjusts the deviations to calculate the steering value
            self.speeds = [80, 70, 50, 40, 35, 15]  # Max speed, medium speed, slow speed
            self.speed_thresholds = [85, 70, 50, 40, 35]  # How big the lane distance has to be to achieve a certain speed
            self.crossing_duration = 3
        elif driving_mode == 0:  # MODE: SLOW
            self.steering_weights = [(30, 0.0), (40, 0.00), (50, 0.0), (60, 0.20), (70, 0.6), (80, 0.1), (90, 0.1), (100, 0.0)]  # How much the deviation at a specific height should weigh # Higher in the picture: Lower number
            self.steering_thresholds = [(0.03, 0.0), (0.22, 0.25), (0.3, 0.35), (0.48, 0.6), (0.4, 0.9)]  # Adjusts the deviations to calculate the steering value
            self.speeds = [15, 10, 8, 5]  # Max speed, medium speed, slow speed
            self.speed_thresholds = [70, 50, 40]  # How big the lane distance has to be to achieve a certain speed
            self.crossing_duration = 9

    def get_movement_params(self, left_lane, right_lane, lane_distance):
        """

        """
        calculated_speed = 5
        calculated_steering = 50
        full_left = 99
        full_right = 1
        filtered_left_lane = [tupel for tupel in left_lane if tupel[0] > 50]
        filtered_right_lane = [tupel for tupel in right_lane if tupel[0] > 50]
        guess_cross_left = [tupel for tupel in left_lane if tupel[0] in (80, 90)]
        guess_cross_right = [tupel for tupel in right_lane if tupel[0] in (80, 90)]

        if not left_lane and not right_lane:
            return calculated_speed, calculated_steering

        if filtered_left_lane and not filtered_right_lane and len(filtered_left_lane)>=2:
            return calculated_speed, full_left

        if filtered_right_lane and not filtered_left_lane and len(filtered_right_lane)>=2:
            return calculated_speed, full_right

        lane_distance = ((HEIGHT - lane_distance) * 100) // HEIGHT

        global CROSSING_DETECTED
        deviations = []
        for height in CHECK_HEIGHTS:
            deviation = find_deviation_at_height(left_lane, right_lane, height)
            if deviation is not None:
                deviations.append((height, deviation))
            else:
                if height == 70 and not CROSSING_DETECTED and lane_distance > 40: # Crossing detected
                    CROSSING_DETECTED = True
                    self.crossing_count = 0

        if CROSSING_DETECTED:
            deviation = find_deviation_at_height(left_lane, right_lane, 50)
            if deviation is None:
                calculated_steering = 50
            else:
                deviation = adjust_deviation(deviation, self.steering_thresholds)
                deviation = deviation * 0.5
                calculated_steering = int(50 - deviation * 50)

        elif not guess_cross_left and not guess_cross_right:
            calculated_steering = self.calculate_steering(deviations) * 0.5
        else:
            calculated_steering = self.calculate_steering(deviations)

        self.crossing_count += 1
        if self.crossing_count > self.crossing_duration:
            CROSSING_DETECTED = False



        calculated_speed = self.calculate_speed(calculated_steering, lane_distance)

        """
        # Testing
        if self.count < 250:
            calculated_speed = 100
        else:
            calculated_speed = 10
        self.count += 1
        """
        # self.set_brake_mode(calculated_speed)
        # if self.brake_mode:
        #    calculated_speed = 0

        self.last_speed = calculated_speed

        return calculated_speed, calculated_steering

    def calculate_steering(self, deviations):
        weight_sum = 0
        total_deviation = 0
        for height, deviation in deviations:
            deviation = adjust_deviation(deviation, self.steering_thresholds)
            _, weight = find_closest_in_range(self.steering_weights, height, height - 10, height + 10)
            deviation *= weight
            weight_sum += weight
            total_deviation += deviation
        if weight_sum < 0.5:
            if len(deviations) >= 2:
                deviations = interpolate_deviations(deviations)
                self.calculate_steering(deviations)
            #print(weight_sum)
        if weight_sum == 0:
            return 50
        total_deviation = total_deviation / weight_sum
        steering = int(50 - total_deviation * 50)
        return min(100, max(0, steering))

    def calculate_speed(self, steering, lane_distance):
        speed = self.speeds[-1]  # Slow speed
        if abs(steering - 50) > 20:  # Steering value is big -> Drive slow
            return speed
        for i in range(len(self.speed_thresholds)):
            if lane_distance > self.speed_thresholds[i]:
                speed = self.speeds[i]
                break
        return speed

    def set_brake_mode(self, speed):
        if speed > self.speed_threshold:  # Speed is above self.speed_threshold, brake mode should be ended
            self.brake_mode = False
            self.brake_mode_count = 0
            return
        if self.last_speed > 0:
            if self.last_speed < self.speed_threshold:  # Speed was above self.speed_threshold previously, should enter brake mode
                self.brake_mode = True
                self.brake_mode_count = 0
                return

        if self.brake_mode_count > self.max_frames_brake_mode:  # Max frames for brake mode reached, disable brake mode
            self.brake_mode = False
            self.brake_mode_count = 0

        self.brake_mode_count += 1