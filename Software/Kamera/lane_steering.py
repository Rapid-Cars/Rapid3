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
threshold_lane1 = (0, 100)
threshold_lane2 = (0, 100)

#ledRed = pyb.LED(1) # Initiates the red led
#ledGreen = pyb.LED(2) # Initiates the green led

clock = time.clock() # Instantiates a clock object
count = 0

while(True):
    clock.tick() # Advances the clock
    img = sensor.snapshot() # Takes a snapshot and saves it in memory

    # Find blobs with a minimal area of 50x50 = 2500 px
    # Overlapping blobs will be merged
    blobs = img.find_blobs([threshold_lane1, threshold_lane2], area_threshold=2500, merge=True)
    count = count
    # Draw blobs
    for blob in blobs:
        # count up
        count += 1

        # Weisen Sie dem ersten Blob den Namen blob1 und dem zweiten den Namen blob2 zu
        if count == 1:
            blob1 = blob
            # draw a rectangle for blob1
            img.draw_rectangle(blob1.rect(), color=(0,255,0))
            # draw a cross in the middle of blob1
            img.draw_cross(blob1.cx(), blob1.cy(), color=(0,255,0))
        elif count == 2:
            blob2 = blob
            # draw a rectangle for blob2
            img.draw_rectangle(blob2.rect(), color=(0,255,0))
            # draw a cross in the middle of blob2
            img.draw_cross(blob2.cx(), blob2.cy(), color=(0,255,0))
        else:
            # Optional: Für alle weiteren Blobs (nach dem zweiten)
            img.draw_rectangle(blob.rect(), color=(255,0,0))  # Rot für weitere Blobs
            img.draw_cross(blob.cx(), blob.cy(), color=(255,0,0))

    # Turn on green LED if a lane (a blob) was found
    if len(blobs) > 1:
        #ledGreen.on()
        #ledRed.off()
        #print("There is a lane!")
        print(blob1.cx(), blob2.cx())
        if blob1.cx()<160 and blob2.cx()>160:
            print("Full speed ahead!", blob1.cx(), blob2.cx())
        if blob1.cx()>80:
            print("Gotta turn right!")
        if blob2.cx()<240:
            print("Gotta turn left!")
    #else:
    # Turn the red LED on if no lane (no blob) was found
        #ledGreen.off()
        #ledRed.on()
        #print("There is no lane!")

    #pyb.delay(50) # Pauses the execution for 50ms
    #print(clock.fps()) # Prints the framerate to the serial console
    #blob1.cx()==81 #attempt in resetting a blob value
    #print(blob1.cx())

    #The program doesn't start unless it finds two blobs in the first attempt.
    #The blob values don't reset after the camera lost one. This leads to the computer not knowing
    #that one blob is lost, which makes problems in controlling the steering.
    #We might use another method instead of blobs, like lines or contours, but we try to make it
    #work first before optimizing it.
