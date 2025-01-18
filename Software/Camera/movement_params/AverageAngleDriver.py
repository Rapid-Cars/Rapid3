import math

def calculate_angle(left_lane, right_lane):
    """
    Calculate the movement parameters (speed and steering angle) based on the average lane angles.

    This function determines the steering angle and speed required for a vehicle by computing
    the average angles of the left and right lanes. The average angle is used to derive a
    coefficient that adjusts the steering angle to keep the vehicle aligned with the road.

    Parameters
    ----------
    left_lane : list of tuple
        A list of tuples representing the coordinates of the left lane boundary.

    right_lane : list of tuple
        A list of tuples representing the coordinates of the right lane boundary.

    Returns
    -------
    tuple
        A tuple containing the calculated speed (int) and steering angle (int).
    """
    left_angle = get_average_lane_angle(left_lane)
    right_angle = get_average_lane_angle(right_lane)
    average_angle = (left_angle + right_angle) / 2

    if len(left_lane) < 2:
        average_angle = right_angle
    elif len(right_lane) < 2:
        average_angle = left_angle

    coefficient = average_angle * 2 * 1.8 / math.pi
    coefficient = coefficient * 2

    steering = 50 * (1 - coefficient)
    steering = int(steering)
    if steering < 0:
        steering = 0
    elif steering > 100:
        steering = 100

    speed = 100

    return speed, steering

def get_average_lane_angle(lane):
    """
        Calculate the average angle of a given lane based on its coordinates.

        This function computes the angles between consecutive points in the lane
        and returns their average. It provides a measure of the lane's direction,
        which can be used to adjust a vehicle's steering angle.

        Parameters
        ----------
        lane : list of tuple
            A list of tuples representing the coordinates of the lane.

        Returns
        -------
        float
            The average angle of the lane in radians.
    """
    angles = [0]
    last_element = None
    for element in lane:
        if last_element is not None:
            """
            y2 > y1
            if x2 = x1 -> 0 (straight line)
            if x2 > x1 -> >0 (right)
            if x2 < x1 -> <0 (left)
            angle = atan[(x2 - x1) / (y2 - y1)]
            """
            angle = math.atan((element[1] - last_element[1]) / (element[0] - last_element[0]))
            # Implement y-factor? ToDo
            angles.append(angle)
        last_element = element
    average_angle = sum(angles) / len(angles)
    return average_angle

class AverageAngleDriver:
    """
    The AverageAngleDriver class determines the vehicle's movement parameters, including speed
    and steering angle, by calculating the average angle of detected lane boundaries.

    The class leverages lane coordinate data to compute the angles of both left and right lanes
    and calculates their average to derive the optimal steering angle. It dynamically adapts
    the vehicle's path to maintain alignment with the road, even when one of the lanes is missing
    or less defined.
    """
    def get_movement_params(self, left_lane, right_lane):
        return calculate_angle(left_lane, right_lane)