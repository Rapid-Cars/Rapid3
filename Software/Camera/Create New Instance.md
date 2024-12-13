# Creating a New Instance of `lane_recognition` or `movement_params`

To create a new instance of `lane_recognition` or `movement_params`, follow the steps below:

---

## Lane Recognition

1. **Navigate to the Directory:**
   Inside the `/Camera/lane_recognition` directory, create a new file named `MyClassName.py`.
   Note: Replace "MyClassName" with the real name of the class.
2. **Code Template:**
   Use the following Python code template inside your new class:

   ```python
   # Constants
   CONSECUTIVE_PIXELS = 5  # Number of pixels in a row for it to count as an edge
   MAX_CONSECUTIVE_PIXELS = CONSECUTIVE_PIXELS * 5  # If exceeded, it won't be counted as a lane
   THRESHOLD = 70  # Darkness threshold, can be constant or dynamically adjusted
   HEIGHT = 240
   WIDTH = 320
   
   class MyClassName:
       """
       ToDo: Describe how your class works here
       """
       def __init__(self):
           self.pixel_getter = None
   
       def setup(self, pixel_getter):
           """
           Initialize with a pixel getter. This function needs to be run once before lane recognition.
           """
           self.pixel_getter = pixel_getter
   
       def recognize_lanes(self, img):
           """
           Recognizes lanes from a provided image by identifying the edges of the lanes
           using a pixel getter utility. The method determines the positions of the left
           and right lanes relative to the midpoint of the image.
   
           Parameters
           ----------
           img : any
               The image from which lanes will be recognized.
   
           Returns
           -------
           tuple
               A tuple containing two lists: `left_lane` and `right_lane`, each representing
               the detected lane edges as determined by the image analysis.
   
           Raises
           ------
           ValueError
               If the pixel getter has not been set up prior to executing lane recognition.
           """
           if not self.pixel_getter:
               raise ValueError("Pixel getter has not been set up. Call setup() first.")
   
           # ToDo: Implement lane recognition algorithm here
           # Use this snippet to get a pixel: pixel = self.pixel_getter.get_pixel(img, x, y)
   ```

---

1. **Important Notes:**
   - Ensure that the `setup` method is called **first** to initialize the `pixel_getter`.
   - Use the method `recognize_lanes(img)` to recognize lanes within an image.
   - The return format must be:

     ```python
     return left_lane, right_lane
     ```

     Where:
     - `left_lane` and `right_lane` are either: 
       - `None` (if no lane is detected), or
       - Arrays of coordinates formatted as `[(y1, x1), (y2, x2)]`.
   - Example:

     ```python
     left_lane = [(100, 50), (200, 60)]
     right_lane = [(100, 270), (200, 260)]
     ```
   - This ensures a consistent and usable lane recognition output.

---

1. **Implementation in** `__init__.py`:

Inside `/Camera/lane_recognition/__init__.py`, do the following:

**4.1. Import the new class:**

```python
# Import the custom class you created
from .MyClassName import MyClassName
```

**4.2. Extend the** `get_lane_recognition_instance(instance)` function:

Navigate to the function `get_lane_recognition_instance(instance)` and add the following condition inside the `if` statement:

```python
# Add this condition to instantiate your new class
elif instance == 'MyClassName':
    return MyClassName()
```

```
Note: This step ensures that `MyClassName` can be dynamically instantiated when `get_lane_recognition_instance(instance)` is called with the appropriate argument.
```

---

Follow the template and guidelines above to implement and customize your specific requirements for lane detection.

## Movement Calculation

1. **Navigate to the Directory:**
   Go to the `/Camera/movement_params` directory and create a new file named `MyClassName.py`.
   Note: Replace "MyClassName" with the real name of the class.
2. **Code Template:**
   Use the following Python code template to define your class:

   ```python
   # Constants
   HEIGHT = 240
   WIDTH = 320
   
   class MyClassName:
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
           # ToDo: Implement movement calculation algorithm here
           return
   ```

---

1. **Important Notes:**
   - The method `get_movement_params(left_lane, right_lane)` is responsible for calculating the **speed** and **steering** based on lane detection.
   - The return format of the method must be:

     ```python
     return speed, steering
     ```

     **Where:**
     - `speed` and `steering` are integer values between `0` and `100`.
     - **Speed:**
       - `0`: Stop
       - `100`: Full speed
     - **Steering:**
       - `0`: Full left
       - `50`: Straight
       - `100`: Full right

---

1. **Implementation in** `__init__.py`:

   To enable dynamic instantiation of your class, update the `/Camera/movement_params/__init__.py` file with the following steps:

   **4.1. Import the new class:**

   ```python
   # Import the custom class you created
   from .MyClassName import MyClassName
   ```

   **4.2. Extend the** `get_movement_params_instance(instance)` function:

   Navigate to the function `get_movement_params_instance(instance)` and add a new condition inside the `if` statement:

   ```python
   # Add this condition to instantiate your new class
   elif instance == 'MyClassName':
       return MyClassName()
   ```

   ***Note****:* This step ensures that `MyClassName` can be dynamically instantiated when `get_movement_params_instance(instance)` is invoked with the corresponding argument.

---

Follow the template and guidelines above to implement and customize your specific requirements for movement calculation.

---

## How to Implement It in Your Code

Import the required packages using:

```python
from Software.Camera.lane_recognition import * # For the OpenMV cam use: libraries.lane_recognition
from Software.Camera.movement_params import * # For the OpenMV cam use: libraries.movement_params
```

Note: The directories `lane_recognition` and `movement_params` have to be moved inside of the directory `libraries` on the OpenMV cam for this to work. 

After completing the steps listed above, use the following code to integrate the new instances into your project:

```python
lane_recognition = get_lane_recognition_instance('NameOfYourClass') #Above: 'MyClassName'
lane_recognition.setup(get_pixel_getter('camera'))  # For the virtual camera, use: 'virtual_cam'
movement_params = get_movement_params_instance('NameOfYourOtherClass') #Above: 'MyClassName'
```

---

Make sure to replace `'NameOfYourClass'` and `'NameOfYourOtherClass'` with the actual names of your lane recognition and movement calculation classes, respectively. This ensures the correct instances are created and initialized.