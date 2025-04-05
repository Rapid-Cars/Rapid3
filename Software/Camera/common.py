FinishLineDetection = None
FinishLineDetected = False

def get_settings():
    """
    Returns the values used for version and algorithm names
    Usable lane_recognition values: CenterLaneFinder, BaseInitiatedDarknessFinder, BaseInitiatedContrastFinder, BaseInitMarc, SobelEdgeDetection, (SobelLaneDistanceDetector)
    Usable movement_params values: CenterLaneDeviationDriver, CenterDeviationDriver, DominantLaneAngleDriver, AverageAngleDriver, StraightAwareCenterLaneDriver
    """
    return {
        "version": "1.0.0",
        "main_lane_recognition": "SobelEdgeDetection",
        "secondary_lane_recognition": "SobelLaneDistanceDetector",
        "movement_params": "StraightAwareCenterLaneDriver",
    }


def update_lane_data(lane, sec_lane):
    """
    Compares the y-values in lane and sec_lane, if there is the same y-value in both Lists
    If both lanes have the same y-value it calculates the average of both x-values.
    If only one lane has a specific y-value it uses the corresponding x-value.
    Afterward it returns the sorted and updated lane data.

    Parameters:
        lane (tuple): The lane of the first algorithm
        sec_lane (tuple): The second lane
    """
    # A dictionary from left lane with y being the Key-value und and x the to the Key-value belonging value.
    lane_dict = {y: x for y, x in lane}

    for y, x in sec_lane:
        if y in lane_dict:
            # Calculates the average if there is the same y-value in both lists and adds it to the dictionary
            lane_dict[y] = (lane_dict[y] + x) // 2
        else:
            # Adds a new element to the dictionary if there is a y-value ONLY existing in sec_lane
            lane_dict[y] = x

    # converts the dictionary into a list.
    updated_lane = sorted(lane_dict.items())
    return updated_lane


def generate_base_name(get_lane_recognition_id, get_movement_params_id):
    """
    Generates a standardized base name for video files based on used algorithms and version.

    Returns:
            - str: A formatted base name string in the form:
                "v{version}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"

            Raises:
            - ValueError: If any provided algorithm name is invalid.
    """
    settings = get_settings()
    lane_recognition_id = get_lane_recognition_id(settings["main_lane_recognition"])
    secondary_lane_recognition_id = get_lane_recognition_id(settings["secondary_lane_recognition"])
    movement_algorithm_id = get_movement_params_id(settings["movement_params"])
    if lane_recognition_id == -1 or movement_algorithm_id == -1:
        raise ValueError("Invalid algorithm name provided.")
    return f"CLIP-v{settings['version']}-LR{lane_recognition_id}-SLR{secondary_lane_recognition_id}-MP{movement_algorithm_id}"


def set_speed_and_steering(img, lane_recognition, secondary_lane_recognition, movement_params, return_lanes=False):
    """
        Calculates speed and steering based on lane recognition and movement parameters.
        Optionally returns lane data for debugging in virtual_cam.
    """
    left_lane, right_lane = lane_recognition.recognize_lanes(img)
    sec_left_lane, sec_right_lane = None, None
    process_left_lane, process_right_lane = left_lane, right_lane
    """
    if secondary_lane_recognition:
        # Use the secondary algorithm only if the main algorithm doesn't recognize enough Elements
        if len(left_lane) + len(right_lane) < 7:
            sec_left_lane, sec_right_lane = secondary_lane_recognition.recognize_lanes(img)
            process_left_lane = update_lane_data(left_lane, sec_left_lane)
            process_right_lane = update_lane_data(right_lane, sec_right_lane)
    """
    lane_distance = secondary_lane_recognition.recognize_lanes(img)
    speed, steering = movement_params.get_movement_params(left_lane, right_lane, lane_distance)
    if FinishLineDetected:
        speed = 0
    if return_lanes:
        return int(speed), int(steering), left_lane, right_lane, [(lane_distance, 80)], sec_right_lane, process_left_lane, process_right_lane
    return int(speed), int(steering)


def setup_lane_recognition(pixel_getter, get_lane_recognition_instance, get_finish_line_detection_instance):
    """
    Initializes lane recognition instances and setups pixel data retrieval.
    """
    settings = get_settings()
    main = get_lane_recognition_instance(settings["main_lane_recognition"])
    main.setup(pixel_getter)
    global FinishLineDetection
    FinishLineDetection = get_finish_line_detection_instance(pixel_getter)
    secondary = get_lane_recognition_instance(settings["secondary_lane_recognition"])
    if secondary:
        secondary.setup(pixel_getter)
    return main, secondary


def setup_movement_params(get_movement_params_instance, mode = 0):
    """
    Initializes the movement parameter instance.
    """
    settings = get_settings()
    return get_movement_params_instance(settings["movement_params"], mode)

def check_for_finish_line(img):
    return
    global FinishLineDetected
    if not FinishLineDetected:
        if FinishLineDetection.check_for_finish_line(img):
            print("Finish line detected.")
            FinishLineDetected = True