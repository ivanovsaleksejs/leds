import sequence

# Sets animation for lamp using parameters provided with GET request
def setSequence(params, globals, config):

    globals.redraw_active = False
    sequenceName = params["sequenceName"] if "sequenceName" in params else globals.sequenceName
    globals.previousData = globals.stripData
    globals.stripData = sequence.getStripData(config["controller"]["deviceID"], sequenceName, globals)
    globals.reset = True

    return "FINE"

# Routes mapping to functions
routes = {
    "sequence": setSequence,
}
