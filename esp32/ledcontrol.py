import time
import gc
import machine
import neopixel

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
def redraw_thread(config, globals):

    # neopixel_write_compressed function treats buffer as elements containing color and length
    # instead of bunch of colors
    # It's very effective if you use one animation for many LEDs
    # This function is available in custom build
    # More info:
    # https://github.com/ivanovsaleksejs/micropython/commit/460708f45bf9ced93bd76a989b599821185a68eb
    if config["useCompressedOutput"]:
        try:
            from esp import neopixel_write_compressed as neopixel_write
            globals.compressedOutput = True
        except:
            from esp import neopixel_write
    else:
        from esp import neopixel_write

    if globals.compressedOutput:
        enum = list(enumerate(globals.stripData))
        bufferSize = len(enum)
    else:
        bufferSize = config["stripCount"] * config["stripLength"]

    np = neopixel.NeoPixel(machine.Pin(config["pinLED"]), bufferSize, timing=1)


    while True:
        if globals.redraw_active:
            redraw_cycle(np, config, globals, neopixel_write)
        else:
            gc.collect()
            time.sleep_ms(100)
        if globals.reset:
            gc.collect()
            globals.reset = False
            globals.redraw_active = True

#
# Function that cycles through strip data and redraws LEDs
#
def redraw_cycle(np, config, globals, neopixel_write):

    enum = list(enumerate(globals.stripData))
    # Align offsets of zones
    for index, strip in enum:
        if globals.compressedOutput:
            strip["animation_data"]["offset"] = index * 5
            if index > 0:
                strip["animation_data"]["offset"] = globals.stripData[index-1]["animation_data"]["zoneEnd"]
            if "flickerTransition" in strip["animation_data"]:
                strip["animation_data"]["zoneEnd"] = strip["animation_data"]["offset"] + 5 * strip["animation_data"]["zoneLength"]
            else:
                strip["animation_data"]["zoneEnd"] = strip["animation_data"]["offset"] + 5
        else:
            strip["animation_data"]["offset"] = sum_lengths(globals.stripData, index)

        # Pass previous animation data (for transitions)
        if globals.previousData:
            strip["animation_data"]["previous"] = globals.previousData[index]["animation_data"]["animations"][globals.previousData[index]["animation_data"]["animation_index"]]

    msPerFrame = int(1000/config["frameRate"])
    frameCount = 0

    # One frame cycle
    while globals.redraw_active:

        # Frame start time
        frameStart = time.ticks_ms()

        np.currentOffset = 0
        #  Process animations
        for index, strip in enum:
            if not "animation_index" in strip["animation_data"]:
                strip["animation_data"]["animation_index"] = 0
            if "done" in strip["animation_data"] and strip["animation_data"]["done"] == True:
                strip["animation_data"]["done"] = False
                if strip["animation_data"]["animation_index"] < len(strip["animation_data"]["animations"]):
                    #strip["animation_data"]["previous"] = strip["animation_data"]["animations"][strip["animation_data"]["animation_index"]]
                    strip["animation_data"]["animations"][strip["animation_data"]["animation_index"]] = False
                    strip["animation_data"]["animation_index"] += 1

            animation = strip["animation_data"]["animations"][strip["animation_data"]["animation_index"]]

            if animation["animation_name"] == "flicker":
                animations.flicker(np, config, index, strip["animation_data"], globals.compressedOutput)
            if animation["animation_name"] == "blink":
                animations.blink(np, config, index, strip["animation_data"], globals.compressedOutput)
            if animation["animation_name"] == "blinkrng":
                animations.blinkrng(np, config, index, strip["animation_data"], globals.compressedOutput)
            if animation["animation_name"] == "blink_solid":
                animations.blink(np, config, index, strip["animation_data"], globals.compressedOutput, True)
            if animation["animation_name"] == "blinkrng_solid":
                animations.blinkrng(np, config, index, strip["animation_data"], globals.compressedOutput, True)
            if animation["animation_name"] == "solid":
                animations.solid(np, config, index, strip["animation_data"], globals.compressedOutput)

            del animation

        del index, strip

        # Send data to LEDs
        neopixel_write(np.pin, np.buf, np.timing)

        # Calculate time spent for frame
        frameTime = time.ticks_diff(time.ticks_ms(), frameStart)

        if frameTime <= msPerFrame:
            time.sleep_ms(msPerFrame - frameTime)

    del enum
    gc.collect()
