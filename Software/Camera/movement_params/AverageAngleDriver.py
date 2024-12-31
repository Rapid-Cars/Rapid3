import math

def calculate_angle(left_lane, right_lane):
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

        def get_movement_params(self, left_lane, right_lane):
            return calculate_angle(left_lane, right_lane)
