# Constants
HEIGHT = 240
WIDTH = 320
THRESHOLD = 60  # Brightness threshold to detect dark pixels (0-255)
TOP_PRECISION = 40      #How close to the top border should be evaluated?
BOTTOM_PRECISION = 240

def get_movement_params(self, left_lane, right_lane):
        """
        Describe how your code operates here

        Parameters
        ----------
        left_lane : list or None
            Coordinates of the left lane or None if no lane is detected.
        right_lane : list or None
            Coordinates of the right lane or None if no lane is detected.

        Returns
        -------
        tuple
            A tuple `(speed, steering)`:
            - `speed`: Integer value (0-100) representing the vehicle's speed.
            - `steering`: Integer value (0-100) representing the steering angle.
        """
        edges1 = []
        edges2 = []
        edges3 = []
        writing_to_edges2 = False  # Flag to track which array to write to
        writing_to_edges3 = False  # Flag to track which array to write to
    
        for x in range(10, 320, 10):  # crossing of longitude
            #img.draw_line(x, DEPTH, x, 240, color=255)
            found_white = False  # Track if a white pixel was found in this column
            for y in range(TOP_PRECISION, BOTTOM_PRECISION):  # Higher start due to worse vision in the distance
                if img.get_pixel(x, y) == 255:  # White pixel due to inversion
                    found_white = True
                    if not writing_to_edges2 and not writing_to_edges3:
                        edges1.append((x, y))
                    elif not writing_to_edges3:
                        edges2.append((x, y))
                    else:
                        edges3.append((x, y))
                    break
            if not found_white and not writing_to_edges2 and len(edges1) > 0:
                writing_to_edges2 = True
            if not found_white and not writing_to_edges3 and len(edges2) > 0:
                writing_to_edges3 = True
    
    
        #print("\nedges1: ", edges1)
        #print("edges2: ", edges2)
    
        longest_array = max([edges1, edges2, edges3], key=len)
    
        angle = 0
        speed = 0
    
        #print("longest_array: ", longest_array)
    
        if len(longest_array) >= 2 and longest_array[-1][1]-longest_array[0][1] != 0:     #calulate the steering with the arctan [x][y]
            img.draw_circle(longest_array[-1][0], longest_array[-1][1], 15, color=255)
            img.draw_circle(longest_array[0][0], longest_array[0][1], 15, color=255)
            angle = math.atan((longest_array[-1][0]-longest_array[0][0]) / (longest_array[-1][1]-longest_array[0][1]))
            coefficient = angle * 2 / 3.1459
    
            steering =  50 * (1 + coefficient)
            speed = 100
            #steering = 50
        else:
            speed = 0
            #speed = 100
            steering = 50
        print("steering:", steering, " speed:", speed, " angle:", angle*180/3.1459, "°")
        #print("angle: ", angle)
        return speed, steering
class move_arctan
    return get_movement_params(self, left_lane, right_lane)
