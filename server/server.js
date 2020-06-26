const app = require('express')()
const redis = require('redis')
const request = require('request')

const usb = require('usb')

import { remoteControllerInit, processRemoteButtons } from './remotecontroller.js'

const redisClient = redis.createClient(6379)

const state = {
  prevButton: false,
  buttonTimeout: false
}

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

/* SERVER INIT */
const server = app.listen(8081, () => {
  const host = server.address().address
  const port = server.address().port
  console.log("Listening at http://%s:%s", host, port)
})

/* REMOTE CONTROLLER INIT */
usb.on('attach', ((usb) => _ => { remoteControllerInit(usb) })(usb))
usb.on('detach', _=>{})

remoteControllerInit()
