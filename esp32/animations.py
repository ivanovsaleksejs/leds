import math
import urandom as random
import gc
import time
import struct


#
# ANIMATION FUNCTIONS
#

#
# Solid color function
#
def solid(np, config, strip_number, strip_data, compressedOutput):

    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]
    if not "drawn" in animation_data or not animation_data["drawn"]:
        strip_data["totalLength"] = strip_data["zoneLength"] * strip_data["stripLength"]
        current_color = animation_data["color"]

        color = [0] * 3
        color[np.ORDER[0]] = int(current_color[0])
        color[np.ORDER[1]] = int(current_color[1])
        color[np.ORDER[2]] = int(current_color[2])

        while True:
            try:
                if compressedOutput:
                    color = struct.pack(">HBBB", strip_data["totalLength"], color[2], color[1], color[0])
                    np.buf[np.currentOffset : np.currentOffset + 5] = color
                else:
                    color = bytearray(color * strip_data["totalLength"])
                    np.buf[strip_data["offset"] * np.bpp : (strip_data["offset"] + strip_data["totalLength"]) * np.bpp] = color
                animation_data["drawn"] = True
                if "time" in animation_data:
                    animation_data["drawTime"] = time.ticks_ms()
            except MemoryError:
                gc.collect()
                continue
            break
    if compressedOutput:
        np.currentOffset += 5
    if "time" in animation_data and "drawTime" in animation_data:
        if time.ticks_ms() - animation_data["drawTime"] >= animation_data["time"]:
            strip_data["done"] =  True


def flicker(np, config, strip_number, strip_data, compressedOutput, solid=False):

    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]

    if "flickerCompleted" in animation_data:
        strip_data["done"] = True
        #intColor = animation_data["flickerColor"]
        #np.buf[animation_data["offset"] : animation_data["offset"] + 5] = struct.pack(">HBBB", animation_data["totalLength"], intColor[2], intColor[1], intColor[0])
    else:
        if "flickerPhaseCompleted" in animation_data and animation_data["flickerPhaseCompleted"] or not "flickerPhaseCompleted" in animation_data:
            if "flickerAll" in animation_data and animation_data["flickerAll"]:
                if "flickerPhaseCompleted" in animation_data and animation_data["flickerPhaseCompleted"]:
                    animation_data["flickerCompleted"] = True
                animation_data["flickerPhaseCompleted"] = False
                animation_data["flickerPhases"] = [(0, 0) for _ in range(0, random.randint(7, 19))]
            else:
                animation_data["flickerPhaseCompleted"] = False
                if not "flickered" in animation_data:
                    animation_data["flickered"] = []
                if "flickerStrip" in animation_data:
                    animation_data["flickered"].append(animation_data["flickerStrip"])
                    del animation_data["flickerStrip"]
                strips = range(0, strip_data["zoneLength"])
                leftStrips = [k for k in strips if k not in animation_data["flickered"]]
                if leftStrips == []:
                    animation_data["flickerCompleted"] = True
                    animation_data["color"] = animation_data["flickerEndColor"]
                else:
                    animation_data["flickerStrip"] = random.choice(leftStrips)

                animation_data["flickerPhases"] = [(random.choice([k for k in range(0,2)] + [k for k in range(0,2)] + [k for k in range(0,2)]), 0) for _ in range(0, random.randint(2, 5))]

            animation_data["flickerPhase"] = 0
            animation_data["flickerToggle"] = 0
            animation_data["flickerStep"] = 0
        else:
            animation_data["flickerStep"] += 1
            if animation_data["flickerStep"] > animation_data["flickerPhases"][animation_data["flickerPhase"]][animation_data["flickerToggle"]]:
                animation_data["flickerStep"] = 0
                animation_data["flickerToggle"] += 1
                if animation_data["flickerToggle"] > 1:
                    animation_data["flickerToggle"] = 0
                    animation_data["flickerPhase"] += 1
                    if animation_data["flickerPhase"] >= len(animation_data["flickerPhases"]):
                        animation_data["flickerPhaseCompleted"] = True

        if "flickerAll" in animation_data and animation_data["flickerAll"]:
            colorTo = animation_data["flickerColor"] if animation_data["flickerToggle"] == 1 else [0, 0, 0]

            # TODO: Fix offfset
            #np.buf[strip_data["offset"] + (strip * 5) : strip_data["offset"] + (strip * 5) + 5] = struct.pack(">HBBB", strip_data["stripLength"], colorTo[1], colorTo[0], colorTo[2])
            np.buf[np.currentOffset : np.currentOffset + 5] = struct.pack(">HBBB", strip_data["stripLength"] * strip_data["zoneLength"], colorTo[1], colorTo[0], colorTo[2])
            np.currentOffset += 5
        else:
            for strip in range(0, strip_data["zoneLength"]):
                if strip in animation_data["flickered"]:
                    colorTo = animation_data["flickerEndColor"]
                elif strip == animation_data["flickerStrip"]:
                    colorTo = animation_data["flickerColor"] if animation_data["flickerToggle"] == 1 else [0, 0, 0]
                else:
                    colorTo = animation_data["flickerStartColor"]

                # TODO: Fix offfset
                #np.buf[strip_data["offset"] + (strip * 5) : strip_data["offset"] + (strip * 5) + 5] = struct.pack(">HBBB", strip_data["stripLength"], colorTo[1], colorTo[0], colorTo[2])
                np.buf[np.currentOffset : np.currentOffset + 5] = struct.pack(">HBBB", strip_data["stripLength"], colorTo[1], colorTo[0], colorTo[2])
                np.currentOffset += 5

#
# Transition function for blink animation
#
def transition(np, config, strip_number, strip_data, compressedOutput, solid=False):

    strip_data["totalLength"] = strip_data["zoneLength"] * strip_data["stripLength"]

    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]

    if not "transition_frame"  in animation_data:
        color = animation_data["color"] if "faded" in animation_data or ("fade_to_black" in animation_data and animation_data["fade_to_black"] == False) else [0,0,0]

        prev = strip_data["previous"]["animation_data"]
        #lazy fix
        if "frames" in prev:
            oldColor = prev["frames"][prev["position"]]

        else:
            oldColor = [0] * 3
            oldColor[np.ORDER[0]] = prev["color"][0]
            oldColor[np.ORDER[1]] = prev["color"][1]
            oldColor[np.ORDER[2]] = prev["color"][2]

        if "faded" in animation_data or ("fade_to_black" in animation_data and animation_data["fade_to_black"] == False):
            oldColor = [0,0,0] if not "fade_to_black" in animation_data or animation_data["fade_to_black"] else oldColor
            #TODO: instead of sleep, need to skip frames
            #time.sleep_ms(animation_data["transitionOffTime"])

            fixColor = [0] * 3
            fixColor[np.ORDER[0]] = color[0]
            fixColor[np.ORDER[1]] = color[1]
            fixColor[np.ORDER[2]] = color[2]
            color = fixColor

        colorDiff = [0] * 3
        colorDiff[np.ORDER[0]] = color[np.ORDER[0]] - oldColor[np.ORDER[0]]
        colorDiff[np.ORDER[1]] = color[np.ORDER[1]] - oldColor[np.ORDER[1]]
        colorDiff[np.ORDER[2]] = color[np.ORDER[2]] - oldColor[np.ORDER[2]]

        transitionTime = animation_data["transitionUpTime"]
        if not "faded" in animation_data:
            transitionTime = animation_data["transitionDownTime"]

        frameCount = int(config["frameRate"] * transitionTime / 1000)
        animation_data["transition_frames_count"] = frameCount
        quots = [0] * 3
        quots[np.ORDER[0]] = colorDiff[np.ORDER[0]] / frameCount
        quots[np.ORDER[1]] = colorDiff[np.ORDER[1]] / frameCount
        quots[np.ORDER[2]] = colorDiff[np.ORDER[2]] / frameCount

        animation_data["transition_quots"] = quots
        animation_data["transition_frame"] = oldColor

        del prev

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
                if compressedOutput:
                    color = struct.pack(">HBBB", strip_data["totalLength"], intColor[2], intColor[1], intColor[0])
                    np.buf[np.currentOffset : np.currentOffset + 5] = color
                    np.currentOffset += 5
                else:
                    color = bytearray(intColor * strip_data["totalLength"])
                    np.buf[animation_data["offset"] * np.bpp : (strip_data["offset"] + strip_data["totalLength"]) * np.bpp] = color
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
    del color
    gc.collect()


def prepareBlink(np, config, strip_number, strip_data, compressedOutput, solid=False):

    strip_data["totalLength"] = strip_data["zoneLength"] * strip_data["stripLength"]

    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]

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
    del color
    del startColor
    del stopColor
    del current_color
    del frameCount
    del animation_time
    del quotient
    gc.collect()


#
# Simple blink function
# Fades from given color to the value defined by quot parameter
# Supports transition from current color to black and back to new blink
#
def blink(np, config, strip_number, strip_data, compressedOutput, solid=False):

    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]
    # Transition effect - goes from current color to black and then to the new color
    if "transition" in animation_data \
        and animation_data["transition"] == 1 \
        and not "transitDone" in animation_data \
        and "previous" in strip_data \
        and ("frames" in strip_data["previous"]["animation_data"] \
                or "color" in strip_data["previous"]["animation_data"] \
             ):
        return transition(np, config, strip_number, strip_data, compressedOutput, solid)

    # We prepare colors once and then draw them
    if not "quotient" in animation_data or not animation_data["quotient"]:
        prepareBlink(np, config, strip_number, strip_data, compressedOutput, solid)
    #
    # Drawing routine
    #
    # When direction is true the animation goes from lowest to the original color
    if not "direction" in animation_data:
        animation_data["direction"] = False
    direction = animation_data["direction"]

    if not "position" in animation_data:
        animation_data["position"] = 0
    position = animation_data["position"]

    if direction and position == 0:
        direction = False
        animation_data["fullCycle"] += 1
        if animation_data["fullCycle"] >= 1 and "onetime" in animation_data and animation_data["onetime"]:
            strip_data["done"] = True

        if solid:
            animation_data["fullCycle"] = 10

    if (not direction) and position >= animation_data["frameCount"] - 1:
        direction = True

    animation_data["direction"] = direction

    # Infinite loop that will repeat an action until no exception is caught
    while True:
        try:
            if compressedOutput:
                intColor = animation_data["frames"][position]
                np.buf[np.currentOffset : np.currentOffset + 5] = struct.pack(">HBBB", strip_data["totalLength"], intColor[2], intColor[1], intColor[0])
                np.currentOffset += 5
            else:
                np.buf[strip_data["offset"] * np.bpp : (strip_data["offset"] + strip_data["totalLength"]) * np.bpp] = bytearray(animation_data["frames"][position] * strip_data["totalLength"])
        except MemoryError:
            gc.collect()
            continue
        break

    if direction:
        position -= 1
    else:
        position += 1

    animation_data["position"] = position


    del direction
    del position
    del intColor

    gc.collect()

#
# Blink with random colors
#

def blinkrng(np, config, strip_number, strip_data, compressedOutput, solid=False):


    animation_data = strip_data["animations"][strip_data["animation_index"]]["animation_data"]
    if not "fullCycle" in animation_data:
        animation_data["fullCycle"] = 0

    if animation_data["fullCycle"] >= 3 or not "color" in animation_data:
        if "quotient" in animation_data:
            del animation_data["quotient"]
        strip_data["previous"] = strip_data["animations"][strip_data["animation_index"]]
        if "transitDone" in animation_data:
            del animation_data["transitDone"]
        if "transition_frame" in animation_data:
            del animation_data["transition_frame"]
        if "transition_frames_count" in animation_data:
            del animation_data["transition_frames_count"]
        if "transition_position" in animation_data:
            del animation_data["transition_position"]
        color = (0, 0, 0)
        animation_data["fullCycle"] = 0
        while max(color) <= 127:
            color = (random.randint(0,8) * 31, random.randint(0,8) * 31, random.randint(0,8) * 31)
        animation_data["color"] = color

        animation_data["quotient"] = False
        animation_data["faded"] = True
        animation_data["fade_to_black"] = False

    blink(np, config, strip_number, strip_data, compressedOutput, solid=solid)
