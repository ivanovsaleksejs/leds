const app = require('express')()
const redis = require('redis')
const request = require('request')

const usb = require('usb')

const redisClient = redis.createClient(6379)

const remoteButtons = {
  "modes": {
    7: "ON",
    135: "OFF"
  },
  "commands": {
    6: "light",
    5: "light_run"
  }
}

let prevButton = false
let buttonTimeout = false

/* ROUTES */
app.get('/registerdevice', (req, res) => {
  let ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress
  if (ip.substr(0, 7) == "::ffff:") {
    ip = ip.substr(7)
  }
  if (redisClient.hget("devices", req.query.id)) {
    redisClient.send_command("hdel", ["devices", req.query.id], () => {
      redisClient.hset("devices", req.query.id, ip, redis.print)
    })
  }
  else {
    redisClient.hset("devices", req.query.id, ip, redis.print)
  }

  res.end(ip)
})

app.get('/getdevices', (req, res) => {
  redisClient.hgetall("devices", (err, devices) => {
    response = devices ? devices : {"error": "list is empty"}
    res.end(JSON.stringify(response))
  })
})

app.get('/setsequence', (req, res) => {
  let sequence = req.query.sequence
  setSequence(sequence)

  res.end('OK')
})

/*
 * Function that sends a name of sequence to all registered devices
 */
const setSequence = (sequence) =>
{
  console.log(sequence)
  redisClient.hgetall("devices", (err, devices) => {
    if (devices) {
      Object.keys(devices).forEach((item) => {
        let rec = (retry) => {
          if (retry >= 10) {
            return
          }
          request("http://" + devices[item] + '/sequence?sequenceName=' + sequence + '&' + Math.random(), (error, response, body) => {
            if (!response) {
              setTimeout(rec, 1000, retry+1)
              return
            }
            response.on('error', (err) => {
              console.log(err)
            })
            if (body != "FINE") {
              setTimeout(rec, 1000, retry+1)
            }
          })
          .on('error', (err) => {
            console.log(err)
          })
        }
        rec(0)
      })
    }
  })
}

/*
 * Initializes remote controller and adds events for buttons
 */
const remoteControllerInit = () =>
{
  let remote = false
  remote = usb.findByIds(6790, 29987) //TODO: move to config or some smarter way
  if (typeof remote == "undefined") {
    return
  }
  remote.open()

  let deviceInterface = remote.interfaces[0]

  if (deviceInterface.isKernelDriverActive()) {
    deviceInterface.detachKernelDriver()
    setTimeout(_=>{}, 2000)
  }

  deviceInterface.claim()
  deviceInterface.endpoints[0].startPoll(1,8)
  deviceInterface.endpoints[0].on("data", processRemoteButtons)
  deviceInterface.endpoints[0].on("error", _=>{}) // Need not to do anything when device is detached as we rerun init once attached back
}

/*
 * Processes remote controller buttons
 */
const processRemoteButtons = (dataBuf) =>
{
  let dataArr = Array.prototype.slice.call(new Uint8Array(dataBuf, 0, 8)) // convert buffer to array
  let pressedButton = [dataArr[0], dataArr[3]]

  if (prevButton+'' != pressedButton) {

    if (buttonTimeout) {
      clearTimeout(buttonTimeout)
    }

    prevButton = pressedButton
    let [mode, command] = [remoteButtons.modes[pressedButton[0]], remoteButtons.commands[pressedButton[1]]]
    if (mode == "OFF" || typeof command == "undefined") {
      setSequence("process")
    }
    else {
      setSequence(command)
    }

    buttonTimeout = setTimeout(_=>{prevButton = false}, 1000)
  }
}

/* SERVER INIT */
const server = app.listen(8081, () => {
  const host = server.address().address
  const port = server.address().port
  console.log("Listening at http://%s:%s", host, port)
})

/* REMOTE CONTROLLER INIT */
usb.on('attach', remoteControllerInit)
usb.on('detach', _=>{})

remoteControllerInit()
