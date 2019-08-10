import json
import esp

#
# Disables esp debug
#
def no_debug():

    esp.osdebug(None)

#
# Reads config file
#
def readConf():
    # Loads config file. Puts secrets in separate variable
    configFile = open('config.json', 'r')
    config = json.loads(configFile.read().replace('\n', ''))
    secrets = config["private"]
    config = config["public"]
    configFile.close()
    return (config, secrets)

# While this variable is true redraw thread runs. Thread terminates once it is false
redraw_active = True
reset = False

# Variable used to adjust delay of each frame
frameTime = 0

# Net connection
net = False

# IP resolved by controller's mDNS domain
controllerIP = False

# Animation variables
sequenceName = "process"
dataFile = ""
stripData = False
previousData = False
compressedOutput = False
