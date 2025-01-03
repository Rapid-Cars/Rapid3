from .CenterDeviationDriver import CenterDeviationDriver
from .DominantLaneAngleDriver import DominantLaneAngleDriver
from .AverageAngleDriver import AverageAngleDriver

def get_movement_params_instance(instance):
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
    if instance == 'CenterDeviationDriver':
        return CenterDeviationDriver()
    elif instance == 'DominantLaneAngleDriver':
        return DominantLaneAngleDriver()
    elif instance == 'AverageAngleDriver':
        return AverageAngleDriver()
    # You can implement new instances here
    else:
        raise ValueError("Unknown process function specified.")
