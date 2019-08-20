import sequence
import gc

# Sets animation for lamp using parameters provided with GET request
def setSequence(params, globals, config):

    globals.redraw_active = False

    sequenceName = params["sequenceName"] if "sequenceName" in params else globals.sequenceName

    for index, strip in list(enumerate(globals.stripData)):
        if "previous" in globals.stripData[index]["animation_data"]:
            del globals.stripData[index]["animation_data"]["previous"]

    globals.previousData = globals.stripData
    tmp = sequence.getStripData(config["controller"]["deviceID"], sequenceName, globals)
    globals.stripData = tmp

    globals.reset = True

    del tmp

    gc.collect()

    return "FINE"

# Routes mapping to functions
routes = {
    "sequence": setSequence,
}
