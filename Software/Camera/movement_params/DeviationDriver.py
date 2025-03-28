import math

HEIGHT = 120
WIDTH = 160

CHECK_HEIGHTS = [35, 50, 60, 75, 81]  # For QQVGA

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
    if -0.1 < deviation < 0.1:
        deviation = 0
    elif deviation > 1:
        deviation = 1
    elif deviation < -1:
        deviation = -1
    return deviation

def adjust_deviation(deviation):
    """Adjusts the deviation based on given steps"""
    thresholds = [(0.13, 0.0), (0.22, 0.15), (0.3, 0.35), (0.35, 0.6), (0.4, 0.9)]

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
    #tolerance = 30
    tolerance = 15
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
        #return calculate_deviation(x_left, WIDTH + 100)
        return calculate_deviation(x_left, WIDTH + 50)
    elif closest_right:
        _, x_right = closest_right
        #return calculate_deviation(-100, x_right)
        return calculate_deviation(-50, x_right)

    # Case 4: Nothing found
    return 0


class CenterLaneDeviationDriver:
    """
    TODO: Documentation
    """

    def __init__(self, driving_mode):
        self.driving_mode = driving_mode

    def get_movement_params(self, left_lane, right_lane):
        """
            Calculate the movement parameters (speed and steering angle) for a vehicle based on lane data.

            This function computes the speed and steering angle that a vehicle
            should adapt to navigate within detected lane boundaries. The
            calculations rely on deviations from the center of the lane to
            determine adjustments in the steering angle and speed.

            Parameters:
                left_lane (list of tuple of int): A list of coordinates representing
                the detected left lane boundary.

                right_lane (list of tuple of int): A list of coordinates representing
                the detected right lane boundary.

            Returns:
                tuple of int: A tuple containing the calculated speed and steering
                angle.
        """
        calculated_speed = 5
        calculated_steering = 50

        if not left_lane and not right_lane:
            return calculated_speed, calculated_steering

        deviation = find_deviation_at_height(left_lane, right_lane, 50)
        deviation = deviation * math.sqrt(abs(deviation)) * 2.6

        calculated_steering = int(50 - deviation * 50)
        # Limit the steering values to 0-100
        if calculated_steering < 0:
            calculated_steering = 0
        if calculated_steering > 100:
            calculated_steering = 100

        calculated_speed = int((1 - abs(deviation)) * 100)
        calculated_speed = int(calculated_speed * 0.5)
        # Limit the speed to values between 10 and 100
        if calculated_speed < 5:
            calculated_speed = 5
        if calculated_speed > 100:
            calculated_speed = 100
        return calculated_speed, calculated_steering


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

        # Constants
        self.max_frames_brake_mode = 10
        self.speed_threshold = 50


    def get_movement_params(self, left_lane, right_lane):
        """

        """
        calculated_speed = 5
        calculated_steering = 50

        if not left_lane and not right_lane:
            return calculated_speed, calculated_steering

        center_lane_deviation = find_deviation_at_height(left_lane, right_lane, CHECK_HEIGHTS[2])
        center_lane_deviation = adjust_deviation(center_lane_deviation)

        mid_lane_deviation = find_deviation_at_height(left_lane, right_lane, CHECK_HEIGHTS[1])
        mid_lane_deviation = adjust_deviation(mid_lane_deviation)

        calculated_steering = int(50 - center_lane_deviation * 50)

        if abs(mid_lane_deviation > 0.25):
            calculated_steering = calculated_steering * 1.5

        # Limit the steering values to 0-100
        if calculated_steering < 0:
            calculated_steering = 0
        if calculated_steering > 100:
            calculated_steering = 100

        #bottom_lane_deviation = find_deviation_at_height(left_lane, right_lane, CHECK_HEIGHTS[2])

        top_lane_deviation = find_deviation_at_height(left_lane, right_lane, CHECK_HEIGHTS[0])
        top_lane_deviation = adjust_deviation(top_lane_deviation)

        speed_factor = 1
        if len(left_lane) < 3 or len(right_lane) < 3:
            speed_factor = speed_factor * 0.8
        if top_lane_deviation > 0.3:
            speed_factor = speed_factor * 0.4
        if mid_lane_deviation > 0.25:
            speed_factor = speed_factor * 0.4
        if abs(top_lane_deviation - center_lane_deviation) > 0.1:
            speed_factor = speed_factor * 0.4

        #speed_factor = self.compute_speed_factor(bottom_lane_deviation, center_lane_deviation, top_lane_deviation)

        calculated_speed = int((1 - abs(center_lane_deviation)) * 100)
        if calculated_speed > 100:
            calculated_speed = 100
        calculated_speed = int(calculated_speed * 1 * speed_factor)
        # Limit the speed to values between 10 and 100
        if calculated_speed < 5:
            calculated_speed = 5
        if calculated_speed > 100:
            calculated_speed = 100
        """
        # Testing
        if self.count < 250:
            calculated_speed = 100
        else:
            calculated_speed = 10
        self.count += 1
        """
        self.set_brake_mode(calculated_speed)
        if self.brake_mode:
            calculated_speed = 0
        if self.driving_mode == 1:
            calculated_speed = int(calculated_speed * 0.5)

        self.last_speed = calculated_speed

        return calculated_speed, calculated_steering

    def set_brake_mode(self, speed):
        if speed > self.speed_threshold: # Speed is above self.speed_threshold, brake mode should be ended
            self.brake_mode = False
            self.brake_mode_count = 0
            return
        if self.last_speed > 0:
            if (speed / self.last_speed) < 0.5: # Speed was above self.speed_threshold previously, should enter brake mode
                self.brake_mode = True
                self.brake_mode_count = 0
                return

        if self.brake_mode_count > self.max_frames_brake_mode: # Max frames for brake mode reached, disable brake mode
            self.brake_mode = False
            self.brake_mode_count = 0

        self.brake_mode_count += 1