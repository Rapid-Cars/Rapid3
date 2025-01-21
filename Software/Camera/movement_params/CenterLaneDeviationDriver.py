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

def find_middle_deviation(left_lane, right_lane):
    # Middle of the picture
    middle = HEIGHT // 2

    # Tolerance for values
    tolerance = 30
    range_min = middle - tolerance
    range_max = middle + tolerance

    # Finds the closest point to the middle
    closest_left = find_closest_in_range(left_lane, middle, range_min, range_max)
    closest_right = find_closest_in_range(right_lane, middle, range_min, range_max)

    # Case 1: Both values exist and the y-values are equal
    if closest_left and closest_right:
        y_left, x_left = closest_left
        y_right, x_right = closest_right
        if y_left == y_right:
            return calculate_deviation(x_left, x_right)

        # Case 2: Both values exist and the y-values are not equal
        # -> Use the value that is closer to the middle
        left_distance = abs(y_left - middle)
        right_distance = abs(y_right - middle)

        if left_distance <= right_distance:
            return calculate_deviation(x_left, WIDTH)
        else:
            return calculate_deviation(0, x_right)

    # Case 3: One value exists and is close to the middle
    if closest_left:
        _, x_left = closest_left
        return calculate_deviation(x_left, WIDTH + 100)
    elif closest_right:
        _, x_right = closest_right
        return calculate_deviation(-100, x_right)

    # Case 4: Nothing found
    return 0



def calculate_movement_params(left_lane, right_lane):
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
    calculated_speed = 10
    calculated_steering = 50

    if not left_lane and not right_lane:
        return calculated_speed, calculated_steering

    deviation = find_middle_deviation(left_lane, right_lane)
    deviation = deviation * 1.9

    calculated_steering = int(50 - deviation * 50)
    # Limit the steering values to 0-100
    if calculated_steering < 0:
        calculated_steering = 0
    if calculated_steering > 100:
        calculated_steering = 100

    calculated_speed = int((1 - abs(deviation)) * 100)
    calculated_speed = int(calculated_speed * 1.5)
    # Limit the speed to values between 10 and 100
    if calculated_speed < 10:
        calculated_speed = 10
    if calculated_speed > 100:
        calculated_speed = 100

    return calculated_speed, calculated_steering


class CenterLaneDeviationDriver:
    """
    TODO: Documentation
    """
    def get_movement_params(self, left_lane, right_lane):
        return calculate_movement_params(left_lane, right_lane)

