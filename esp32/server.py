import network
import usocket as socket
import urequests
import ure as re
import json
import random
import time
import gc

import minimalmdns
from routes import routes

def lookup_network(net, networks):
    ssid = bytearray(net["ssid"])
    for n in networks:
        if n[0] == ssid:
            return net
    return False

# Connect to wifi
def connect(secrets, config, globals):

    globals.net = network.WLAN(network.STA_IF)

    if not globals.net.isconnected():
        globals.net.active(True)
        networks = globals.net.scan()
        for s in secrets["networks"]:
            name = lookup_network(s, networks)
            if name != False:
                globals.net.connect(name["ssid"], name["password"])
                while not globals.net.isconnected():
                    pass
                break

    globals.controllerIP = getControllerIP(config["controllerHostname"], globals.net)

    print(globals.net.ifconfig())
    print(globals.controllerIP)

    registerDevice(globals.controllerIP, config, globals.net.ifconfig()[0])

def getControllerIP(hostname, net):

    controllerIP = ""
    while controllerIP == "":
        time.sleep(1)
        controllerIP = minimalmdns.mdnshostnametoipnumber(net, hostname)

    return controllerIP

def registerDevice(ip, config, thisIP):

    txt = ""
    url = config["controller"]["protocol"] \
                + ip \
                + config["controller"]["port"] \
                + config["controller"]["registerPath"] \
                + '?id=' \
                + config["controller"]["deviceID"] \
                + '&foo=' \
                + str(random.random())

    while not txt == thisIP:
        while True:
            try:
                r = urequests.get(url)
            except:
                time.sleep(1)
                continue

            txt = r.text
            break

    print(txt)



# Parse GET parameters
def qs_parse(qs):

    parameters = {}
    ampersandSplit = qs.split("&")

    for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = equalSplit[1] if len(equalSplit) == 2 else equalSplit[0]

    return parameters

# Process GET request
def get(path):

    route = path
    params = []
    pos = path.find('?')
    fname = path

    if pos > -1:
        fname = path[0:pos]
        params = qs_parse(path[pos+1:])

    route = list(filter(lambda x: not x == "", fname.split('/')))

    return {"cmd": "get", "route": route, "params": params}

# Socket server

def server(config, globals):

    s = False
    while True:
        if not s:
            addr = socket.getaddrinfo(globals.net.ifconfig()[0], 80)[0][-1]
            s = socket.socket()
            s.bind(addr)
            s.listen(1)
            s.settimeout(None)

        try:
            conn,addr=s.accept()
            request=conn.recv(4096)

            request = re.compile('\r?\n').split(request.decode('utf-8'))
            method,path,protocol = request[0].split()

            response = ""

            parseGet = get(path)

            if parseGet["cmd"] == "get" and parseGet["route"][0] in routes:
                response = routes[parseGet["route"][0]](parseGet["params"], globals, config)
            print("ok")

        except:
            print("fail")
            continue

        try:
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        except:
            print("fail2")
            gc.collect()

        conn.close()
