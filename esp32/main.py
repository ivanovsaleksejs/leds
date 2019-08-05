import _thread
import machine
import neopixel

import globals
import ledcontrol
import sequence
import server

globals.no_debug()

(config, secrets) = globals.readConf()

np = neopixel.NeoPixel(machine.Pin(config["pinLED"]), config["stripCount"] * config["stripLength"], timing=1)

sequence.loadStripData(config["dataFile"], globals)

globals.stripData = sequence.getStripData(config["controller"]["deviceID"], config["defaultSequence"], globals)

_thread.start_new_thread(ledcontrol.redraw_thread, (np, config, globals))

server.connect(secrets, config, globals)

_thread.start_new_thread(server.server, (config, globals))
