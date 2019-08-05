import json

#
# Loads data from JSON file
#
def loadStripData(filename, globals):
    dataFile = open(filename, 'r')
    globals.dataFile = dataFile.read().replace('\n', '')
    dataFile.close()

#
# Returns strip data for specific animation
#
def getStripData(deviceName, sequenceName, globals):
    data = json.loads(globals.dataFile)
    return data[sequenceName][deviceName]
