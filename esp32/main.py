import _thread

import globals
import ledcontrol
import sequence
import server

globals.no_debug()

(config, secrets) = globals.readConf()

sequence.loadStripData(config["dataFile"], globals)

globals.stripData = sequence.getStripData(config["controller"]["deviceID"], config["defaultSequence"], globals)

_thread.start_new_thread(ledcontrol.redraw_thread, (config, globals))

server.connect(secrets, config, globals)

_thread.start_new_thread(server.server, (config, globals))
