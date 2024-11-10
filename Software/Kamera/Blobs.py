# Untitled - By: maisb - Tue Nov 5 2024

#import pyb # Import module for board related functions
import sensor # Import the module for sensor related functions
import image # Import module containing machine vision algorithms
import time # Import module for tracking elapsed time

sensor.reset() # Resets the sensor
sensor.set_pixformat(sensor.GRAYSCALE) # Sets the sensor to RGB
sensor.set_framesize(sensor.QVGA) # Sets the resolution to 320x240 px

sensor.skip_frames(time = 2000) # Skip some frames to let the image stabilize

# Define the min/max LAB values we're looking for
threshold_lane1 = (24, 60)
threshold_lane2 = (24, 60)

#ledRed = pyb.LED(1) # Initiates the red led
#ledGreen = pyb.LED(2) # Initiates the green led

clock = time.clock() # Instantiates a clock object

while(True):
    clock.tick() # Advances the clock
    img = sensor.snapshot() # Takes a snapshot and saves it in memory

    # Find blobs with a minimal area of 50x50 = 2500 px
    # Overlapping blobs will be merged
    blobs = img.find_blobs([threshold_lane1, threshold_lane2], area_threshold=2500, merge=True)

    # Draw blobs
    for blob in blobs:
        # Draw a rectangle where the blob was found
        img.draw_rectangle(blob.rect(), color=(0,255,0))
        # Draw a cross in the middle of the blob
        img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))

    # Turn on green LED if a lane (a blob) was found
    if len(blobs) > 0:
        #ledGreen.on()
        #ledRed.off()
        print("There is a lane!")
    else:
    # Turn the red LED on if no lane (no blob) was found
        #ledGreen.off()
        #ledRed.on()
        print("There is no lane!")

    #pyb.delay(50) # Pauses the execution for 50ms
    #print(clock.fps()) # Prints the framerate to the serial console
