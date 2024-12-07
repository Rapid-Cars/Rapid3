from .LaneRecognitionOne import LaneRecognitionOne
from .LaneRecognitionTwo import LaneRecognitionTwo


class PixelGetter:
    """
    Provides functionality for retrieving pixel information from an image.

    The PixelGetter class serves as a base class for extracting pixel data
    from images. Intended to be subclassed with specific implementations
    depending on the image format or library used, this class defines a
    contract for the get_pixel method, which is expected to be implemented
    with logic to access a pixel at a given coordinate.

    Methods
    -------
    get_pixel(img, x, y)
        Abstract method intended to return the color of the pixel at the
        specified (x, y) coordinate in the provided image.
    """
    def get_pixel(self, img, x, y):
        raise NotImplementedError("You need to implement this method.")


class CameraPixelGetter(PixelGetter):
    """
    The CameraPixelGetter class is a specialized implementation of the PixelGetter
    interface for retrieving pixel data from a camera image.
    """
    def get_pixel(self, img, x, y):
        return img.get_pixel(x, y)


class VirtualCamPixelGetter(PixelGetter):
    """
        The CameraPixelGetter class is a specialized implementation of the PixelGetter
        interface for retrieving pixel data from a frame of a video stream.
    """
    def get_pixel(self, img, x, y):
        return img[y, x]


def get_pixel_getter(type_name):
    """
    Determines and returns the appropriate pixel getter object based on
    the given type name.

    This function facilitates the retrieval of pixel information by
    selecting the appropriate pixel getter object, such as 'camera' or
    'virtual_cam'. A ValueError is raised if the specified type name
    does not match any known pixel getter types.

    Parameters:
    type_name (str): A string indicating the type of pixel getter to
    retrieve. Accepted values are 'camera' and 'virtual_cam'.

    Returns:
    object: An instance of the pixel getter class corresponding to
    the type name.

    Raises:
    ValueError: If the type name provided does not match any known
    pixel getter types.
    """
    if type_name == 'camera':
        return CameraPixelGetter()
    elif type_name == 'virtual_cam':
        return VirtualCamPixelGetter()
    else:
        raise ValueError("Unknown pixel getter type specified.")


def get_lane_recognition_instance(instance):
    """
    Get an instance of a lane recognition class based on the given string identifier.

    This function returns an instance of a lane recognition class specified by
    the given instance identifier. It currently supports two lane recognition
    classes: 'LaneRecognitionOne' and 'LaneRecognitionTwo'. The function can be
    easily extended to support additional lane recognition classes by adding
    additional conditions for new identifiers.

    Parameters:
        instance: str
            A string identifier for the lane recognition class to instantiate. It
            can be either 'LaneRecognitionOne' or 'LaneRecognitionTwo'. If a
            different value is provided, the function will raise a ValueError.

    Returns:
        LaneRecognition:
            An instance of the lane recognition class corresponding to the given
            identifier. The type of the object returned depends on the value of
            the instance parameter.

    Raises:
        ValueError:
            If the provided instance identifier does not match any known lane
            recognition class, a ValueError is raised with a message indicating
            the issue.
    """
    if instance == 'LaneRecognitionOne':
        return LaneRecognitionOne()
    elif instance == 'LaneRecognitionTwo':
        return LaneRecognitionTwo()
    # You can implement new instances here
    else:
        raise ValueError("Unknown process function specified.")
