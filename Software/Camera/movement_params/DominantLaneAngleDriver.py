import math

def calculate_angle(left_lane, right_lane):
    """
        Calculate the steering angle and speed adjustment based on lane data.

        This function determines the steering angle and adjusts the speed of
        a vehicle based on the detected left and right lane markings. The
        calculations consider the longest detected lane data and use trigonometric
        principles to compute the adjustments. Defaults are returned if no
        sufficient lane data is available.

        Parameters:
            left_lane (list[tuple[int, int]]): Coordinates of the detected
                points on the left lane marking.
            right_lane (list[tuple[int, int]]): Coordinates of the detected
                points on the right lane marking.

        Returns:
            tuple[int, int]: A tuple where the first value represents the
            adjusted speed, and the second value represents the adjusted steering angle.
    """
    steering = 50
    speed = 5

    longest_array = max([left_lane, right_lane], key=len)

    if not longest_array or len(longest_array) < 2:
        # If no valid lane is found or the lane data is insufficient, return defaults
        return speed, steering

    dif = longest_array[-1][0] - longest_array[0][0]

    if dif != 0:
        angle = math.atan((longest_array[-1][1] - longest_array[0][1]) / dif)
        coefficient = angle * 2 / math.pi
        coefficient = coefficient * 1.8

        steering = 50 * (1 - coefficient)
        speed = 100 - 2 * abs(50 - steering)
        if speed < 10:
            speed = 10
    return speed, steering


class DominantLaneAngleDriver:
        """
        This class calculates the angle of the dominant (longest) lane.
        Based on this angle, the vehicle steering angle is adjusted.
        The speed is adjusted based on the steering angle
        """
        def get_movement_params(self, left_lane, right_lane):
            """
            Calculates the movement parameters based on the given lane positions.

            This method determines the angle required for proper alignment by utilizing
            the provided lane line positions on the left and the right.

            Args:
                left_lane (list): A list of points representing the left lane.
                right_lane (list): A list of points representing the right lane.

            Returns:
                float: The calculated angle for lane alignment.
            """

            return calculate_angle(left_lane, right_lane)
