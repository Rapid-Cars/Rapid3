HEIGHT = 240
WIDTH = 320


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
    tolerance = 30
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
        return calculate_deviation(x_left, WIDTH + 100)
    elif closest_right:
        _, x_right = closest_right
        return calculate_deviation(-100, x_right)

    # Case 4: Nothing found
    return 0


class CenterLaneDeviationDriver:
    """
    TODO: Documentation
    """
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

        deviation = find_deviation_at_height(left_lane, right_lane, 120)
        deviation = deviation * abs(deviation) * 2.1

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
    def get_movement_params(self, left_lane, right_lane):
        """

        """
        calculated_speed = 5
        calculated_steering = 50

        if not left_lane and not right_lane:
            return calculated_speed, calculated_steering

        center_lane_deviation = find_deviation_at_height(left_lane, right_lane, 120)
        center_lane_deviation = center_lane_deviation  * 3

        calculated_steering = int(50 - center_lane_deviation * 50)
        # Limit the steering values to 0-100
        if calculated_steering < 0:
            calculated_steering = 0
        if calculated_steering > 100:
            calculated_steering = 100

        bottom_lane_deviation = find_deviation_at_height(left_lane, right_lane, 200)

        top_lane_deviation = find_deviation_at_height(left_lane, right_lane, 40)

        speed_factor = self.compute_speed_factor(bottom_lane_deviation, center_lane_deviation, top_lane_deviation)

        calculated_speed = int((1 - abs(center_lane_deviation)) * 100)
        calculated_speed = int(calculated_speed * 0.5 * speed_factor)
        # Limit the speed to values between 10 and 100
        if calculated_speed < 5:
            calculated_speed = 5
        if calculated_speed > 100:
            calculated_speed = 100
        return calculated_speed, calculated_steering

    def compute_speed_factor(self, bottom_lane_deviation, center_lane_deviation, top_lane_deviation):
        straight_deviation_threshold = 0.1  # Tolerance for "close to 0"


        deviation_difference = abs(bottom_lane_deviation - top_lane_deviation)

        # Case 1: Perfectly centered and straight road
        if (abs(bottom_lane_deviation) < straight_deviation_threshold
                and abs(center_lane_deviation) < straight_deviation_threshold
                and abs(top_lane_deviation) < straight_deviation_threshold):
            return 2.0  # Maximum speed

        # Case 2: Slight deviation, but straight road
        if deviation_difference < 0.05:
            if abs(center_lane_deviation) < 0.2:
                return 1.9  # Almost max speed
            return 1.7  # Still fast but safer

        # Case 3: Stronger deviation, but still a straight road
        if 0.1 <= deviation_difference < 0.2:
            return 1.5  # Moderate speed to allow correction

        # Case 4: Curve detected (top and bottom deviation differ significantly)
        if deviation_difference >= 0.2:
            if abs(center_lane_deviation) > 0.3:
                return 1.2  # Slow speed for safe cornering
            return 1.4  # Slightly faster if not too far off center

        return 1.0  # Default safe speed if no clear case applies
