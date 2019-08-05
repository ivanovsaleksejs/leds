import math
import random
import gc
import time

#
# ANIMATION FUNCTIONS
#

#
# Solid color function
#
def solid(np, config, strip_number, animation_data):

    if not "drawn" in animation_data or not animation_data["drawn"]:
        animation_data["totalLength"] = animation_data["zoneLength"] * animation_data["stripLength"]
        current_color = animation_data["color"]

        color = [0] * 3
        color[np.ORDER[0]] = config["gamma"][int(current_color[0])]
        color[np.ORDER[1]] = config["gamma"][int(current_color[1])]
        color[np.ORDER[2]] = config["gamma"][int(current_color[2])]

        while True:
            try:
                color = bytearray(color * animation_data["totalLength"])
                np.buf[animation_data["offset"] * np.bpp : (animation_data["offset"] + animation_data["totalLength"]) * np.bpp] = color
                animation_data["drawn"] = True
            except MemoryError:
                gc.collect()
                continue
            break

#
# Simple blink function
# Fades from given color to the value defined by quot parameter
# Supports transition from current color to black and back to new blink
#
def blink(np, config, strip_number, animation_data, half=True, pulse=False, solid=False):

    if "transition" in animation_data \
        and animation_data["transition"] == 1 \
        and not "transitDone" in animation_data \
        and "previous" in animation_data \
        and ("frames" in animation_data["previous"] \
                or "color" in animation_data["previous"] \
             ):
        animation_data["totalLength"] = animation_data["zoneLength"] * animation_data["stripLength"]
        if not "transition_frame"  in animation_data:
            color = animation_data["color"] if "faded" in animation_data else [0,0,0]
            #lazy fix
            if "frames" in animation_data["previous"]:
                oldColor = animation_data["previous"]["frames"][animation_data["previous"]["position"]]
            else:
                oldColor = [0] * 3
                oldColor[np.ORDER[0]] = animation_data["previous"]["color"][0]
                oldColor[np.ORDER[1]] = animation_data["previous"]["color"][1]
                oldColor[np.ORDER[2]] = animation_data["previous"]["color"][2]

            if "faded" in animation_data:
                oldColor = [0,0,0]
                time.sleep_ms(800)

            colorDiff = [0] * 3
            colorDiff[np.ORDER[0]] = color[np.ORDER[0]] - oldColor[np.ORDER[0]]
            colorDiff[np.ORDER[1]] = color[np.ORDER[1]] - oldColor[np.ORDER[1]]
            colorDiff[np.ORDER[2]] = color[np.ORDER[2]] - oldColor[np.ORDER[2]]

            transitionTime = animation_data["transitionTime"]
            if not "faded" in animation_data:
                transitionTime /= 10

            frameCount = int(config["frameRate"] * transitionTime / 1000)
            animation_data["transition_frames_count"] = frameCount
            quots = [0] * 3
            quots[np.ORDER[0]] = colorDiff[np.ORDER[0]] / frameCount
            quots[np.ORDER[1]] = colorDiff[np.ORDER[1]] / frameCount
            quots[np.ORDER[2]] = colorDiff[np.ORDER[2]] / frameCount

            animation_data["transition_quots"] = quots
            animation_data["transition_frame"] = oldColor

        else:
            if not "transition_position" in animation_data:
                animation_data["transition_position"] = 0

            oldColor = animation_data["transition_frame"]
            newColor = [0] * 3
            newColor[np.ORDER[0]] = oldColor[np.ORDER[0]] + animation_data["transition_quots"][np.ORDER[0]]
            newColor[np.ORDER[1]] = oldColor[np.ORDER[1]] + animation_data["transition_quots"][np.ORDER[1]]
            newColor[np.ORDER[2]] = oldColor[np.ORDER[2]] + animation_data["transition_quots"][np.ORDER[2]]
            animation_data["transition_frame"] = newColor
            intColor = [int(newColor[0]), int(newColor[1]), int(newColor[2])]

            while True:
                try:
                    color = bytearray(intColor * animation_data["totalLength"])
                    np.buf[animation_data["offset"] * np.bpp : (animation_data["offset"] + animation_data["totalLength"]) * np.bpp] = color
                except MemoryError:
                    gc.collect()
                    continue
                break
            animation_data["transition_position"] += 1

            if animation_data["transition_position"] >= animation_data["transition_frames_count"]:
                if "faded" in animation_data:
                    animation_data["transitDone"] = True
                else:
                    animation_data["transition_position"] = 0
                    animation_data["faded"] = True
                    del animation_data["transition_frame"]

        return

    if not "quotient" in animation_data or not animation_data["quotient"]:

        animation_data["totalLength"] = animation_data["zoneLength"] * animation_data["stripLength"]

        animation_time = animation_data["speed"]

        # For random blinking - resets full cycle counter
        animation_data["fullCycle"] = 0

        frameCount = int(config["frameRate"] * animation_time / 1000)
        animation_data["frameCount"] = frameCount

        current_color = animation_data["color"]
        color = [0] * 3
        color[np.ORDER[0]] = int(current_color[0])
        color[np.ORDER[1]] = int(current_color[1])
        color[np.ORDER[2]] = int(current_color[2])

        #color = bytearray(color)

        if solid:
            animation_data["frames"] = [color for _ in range (0, frameCount+1)]

        else:
            animation_data["frames"] = [color]

            startColor = max(animation_data["color"])
            stopColor = startColor * float(animation_data["quot"])


            for i in range(0, frameCount):
                # Sinusoidal function that generates quotients used to divide start color on them
                quotient = 2 * startColor / (math.cos(i * math.pi / frameCount) * (startColor - stopColor) + startColor + stopColor)

                color = [0] * 3
                color[np.ORDER[0]] = int(current_color[0] / quotient)
                color[np.ORDER[1]] = int(current_color[1] / quotient)
                color[np.ORDER[2]] = int(current_color[2] / quotient)
                #color = bytearray(color)

                animation_data["frames"].append(color)

        animation_data["quotient"] = True





    # When direction is true the animation goes from black to the original color
    if not "direction" in animation_data:
        animation_data["direction"] = False
    direction = animation_data["direction"]

    if not "position" in animation_data:
        animation_data["position"] = 0
    position = animation_data["position"]

    if direction and position == 0:
        direction = False
        animation_data["fullCycle"] += 1

        if solid:
            animation_data["fullCycle"] = 10

    if (not direction) and position >= animation_data["frameCount"] - 1:
        direction = True

    animation_data["direction"] = direction

    # Infinite loop that will repeat an action until no exception is caught
    while True:
        try:
            color = bytearray(animation_data["frames"][position] * animation_data["totalLength"])
            np.buf[animation_data["offset"] * np.bpp : (animation_data["offset"] + animation_data["totalLength"]) * np.bpp] = color
        except MemoryError:
            gc.collect()
            continue
        break

    if direction:
        position -= 1
    else:
        position += 1

    animation_data["position"] = position

    gc.collect()

#
# Blink with random colors
#

def blinkrng(np, config, strip_number, animation_data, half=True, pulse=False, solid=False):

    if not "fullCycle" in animation_data:
        animation_data["fullCycle"] = 0

    if animation_data["fullCycle"] >= 10:
        color = (0, 0, 0)
        while max(color) < 252:
            color = (random.randint(0,4) * 63, random.randint(0,4) * 63, random.randint(0,4) * 63)
        animation_data["speed"] = animation_data["speed"] if solid else random.randint(9, 36) * 200
        animation_data["color"] = color

        animation_data["quotient"] = False

    blink(np, config, strip_number, animation_data, half=half, pulse=pulse, solid=solid)
