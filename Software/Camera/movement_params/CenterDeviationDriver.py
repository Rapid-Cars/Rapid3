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


def calculate_center_deviations(left_lane, right_lane):
    """
    Calculate the deviations between the left and right lane boundaries based on their y and x coordinates.
    This function compares the y coordinates of each lane, calculates deviations when the y coordinates are
    either unequal or equal, and handles remaining entries when one list is fully traversed before the other.

    Parameters:
        left_lane: List[Tuple[int, int]]
            A list of tuples representing y and x coordinates for the left lane boundary.
        right_lane: List[Tuple[int, int]]
            A list of tuples representing y and x coordinates for the right lane boundary.

    Returns:
        List[Tuple[int, Any]]
            A list of tuples where each tuple consists of a y coordinate and the calculated deviation
            between the corresponding x coordinates of the left and right lane boundaries.
    """
    deviations = []

    left_index, right_index = 0, 0
    left_border_len = len(left_lane)
    right_border_len = len(right_lane)

    while left_index < left_border_len and right_index < right_border_len:
        if left_lane[left_index] is not None:
            left_y, left_x = left_lane[left_index]
        else:
            left_index += 1
            break

        if right_lane[right_index] is not None:
            right_y, right_x = right_lane[right_index]
        else:
            right_index += 1
            break

        if left_y > right_y:
            # Different action when left y > right y
            # Implement your specific action here
            deviations.append((left_y, calculate_deviation(left_x, WIDTH)))
            left_index += 1
        elif right_y > left_y:
            # Different action when right y > left y
            # Implement your specific action here
            deviations.append((left_y, calculate_deviation(0, right_x)))
            right_index += 1
        else:
            # Compare the x values when y is identical
            deviations.append((left_y, calculate_deviation(left_x, right_x)))
            left_index += 1
            right_index += 1

    # Handle any remaining left y values with no matching right y.
    while left_index < left_border_len:
        if left_lane[left_index] is not None:
            left_y, left_x = left_lane[left_index]
            deviations.append((left_y, calculate_deviation(left_x, WIDTH + 100)))
        left_index += 1

    # Handle any remaining right y values with no matching left y.
    while right_index < right_border_len:
        if right_lane[right_index] is not None:
            right_y, right_x = right_lane[right_index]
            deviations.append((right_y, calculate_deviation(-100, right_x)))
        right_index += 1

    return deviations


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

    center_deviations = calculate_center_deviations(left_lane, right_lane)
    if not center_deviations:
        return calculated_speed, calculated_steering
    average_deviation = 0
    for deviation in center_deviations:
        average_deviation += deviation[1]
    average_deviation = average_deviation / len(center_deviations)
    average_deviation = average_deviation * abs(average_deviation) * 2.1

    calculated_steering = int(50 - average_deviation * 50)
    if calculated_steering < 0:
        calculated_steering = 0
    if calculated_steering > 100:
        calculated_steering = 100

    calculated_speed = int((1 - abs(average_deviation)) * 100)
    calculated_speed = int(calculated_speed * 6)
    if calculated_speed < 10:
        calculated_speed = 10
    if calculated_speed > 100:
        calculated_speed = 100

    return calculated_speed, calculated_steering


class CenterDeviationDriver:
    """
    The CenterDeviationDriver class determines the vehicle's speed and steering angle by
    utilizing calculated deviations from the lane center. It processes these deviations
    to evaluate how far the vehicle is from being centrally aligned and adjusts the
    parameters accordingly. This approach ensures the vehicle maintains an optimal
    path by dynamically adapting to detected lane boundaries.

    When only one lane is present it assumes an artificial boundary on the missing side
    to compute the center deviation. When both lanes are present, deviations for each
    matching pair (or remaining unmatched points) are calculated. Lastly, it averages
    these deviations to determine the final steering and speed adjustments, ensuring
    smooth and precise navigation.
    """
    def get_movement_params(self, left_lane, right_lane):
        return calculate_movement_params(left_lane, right_lane)

    def calculate_center_deviations(self, left_lane, right_lane):
        return calculate_center_deviations(left_lane, right_lane)