import time
import gc

import animations

#
# Returns time in ms
#
def time_ms():

    return int(time.time()%1000*1000)

#
# Calculates the offset of current zone by summing up the lengths of all previous zones
#
def sum_lengths(stripData, index):

    sum = 0

    for i in range(0, index):
        sum += stripData[i]["animation_data"]["zoneLength"] * stripData[i]["animation_data"]["stripLength"]

    return sum

#
# Thread that runs through animation data and updates np list
#
def redraw_thread(np, config, globals):

    while True:
        if globals.redraw_active:
            redraw_cicle(np, config, globals)
        else:
            gc.collect()
            time.sleep_ms(100)
        if globals.reset:
            globals.reset = False
            globals.redraw_active = True

#
# Function that cycles through strip data and redraws LEDs
#
def redraw_cicle(np, config, globals):

    enum = list(enumerate(globals.stripData))

    # Align offsets of zones
    for index, strip in enum:
        strip["animation_data"]["offset"] = sum_lengths(globals.stripData, index)
        # Pass previous animation data (for transitions)
        if globals.previousData:
            strip["animation_data"]["previous"] = globals.previousData[index]["animation_data"]

    msPerFrame = int(1000/config["frameRate"])
    frameCount = 0

    # One frame cycle
    while globals.redraw_active:

        # Frame start time
        frameStart = time.ticks_ms()

        #  Process animations
        for index, strip in enum:
            if strip["animation_name"] == "blink":
                animations.blink(np, config, index, strip["animation_data"])
            if strip["animation_name"] == "blinkrng":
                animations.blinkrng(np, config, index, strip["animation_data"])
            if strip["animation_name"] == "blink_solid":
                animations.blink(np, config, index, strip["animation_data"], True, False, True)
            if strip["animation_name"] == "blinkrng_solid":
                animations.blinkrng(np, config, index, strip["animation_data"], True, False, True)
            if strip["animation_name"] == "solid":
                animations.solid(np, config, index, strip["animation_data"])

        # Send data to LEDs
        np.write()

        # Calculate time spent for frame
        frameTime = time.ticks_diff(time.ticks_ms(), frameStart)

        if frameTime <= msPerFrame:
            time.sleep_ms(msPerFrame - frameTime)
