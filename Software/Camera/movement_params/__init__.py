from .StraightAwareCenterLaneDriver import StraightAwareCenterLaneDriver

def get_movement_params_instance(instance, driving_mode):
    """
    Retrieve an instance of a movement parameters class based on the given
    instance name. This function serves as a factory method to dynamically
    create objects of different classes that represent movement parameters.
    New instances can be added by extending the conditional checks.

    Parameters:
    instance : str
        The name of the instance to be created. It should match the class
        name of the desired movement parameters object.

    Returns:
    CenterDeviationDriver or DominantLaneAngleDriver
        Returns an instance of the class specified by the 'instance'
        parameter.

    Raises:
    ValueError
        If the 'instance' parameter does not match any known class name.
    """
    if instance == 'StraightAwareCenterLaneDriver':
        return StraightAwareCenterLaneDriver(driving_mode)
    # You can implement new instances here
    else:
        raise ValueError("Unknown process function specified.")


def get_movement_params_id(instance_name):
    """
        Retrieves the movement parameter ID corresponding to a given instance name.

        This function maps specific movement algorithms (represented by their instance names)
        to unique numeric IDs. If the provided instance name does not match any predefined
        algorithm, the function returns a default value of -1.

        Parameters:
            instance_name (str): The name of the movement algorithm instance to retrieve the ID for.

        Returns:
            int: The numeric ID corresponding to the instance name, or -1 if the name is not found.
    """
    movement_algorithm_id = {
        "StraightAwareCenterLaneDriver": 4
    }.get(instance_name, -1)  # Default to -1 if not found
    return movement_algorithm_id