const app = require('express')()
const redis = require('redis')
const request = require('request')

const usb = require('usb')
const SerialPort = require('serialport')

require("regenerator-runtime/runtime");

import config from './config.json'

import { remoteControllerInit, processRemoteButtons } from './remotecontroller.js'

import { setSequence, processSequences } from './sequences.js'

const state = {
  prevButton: false,
  buttonTimeout: false,
  redisClient: redis.createClient(6379),
  sequences: {},
  currentSequences: {},
  serialport: new SerialPort('/dev/ttyS0', {
      baudRate: config.uart_baudrate
  })
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

const process = async () => {
  let a = new Date()
  while (true) {
    let start = a.getTime()		
    processSequences(state)
    a = new Date()
    let end = a.getTime()
    let diff = end - start
    await sleep(Math.min(diff, 30))
  }
}

/* ROUTES */
app.get('/registerdevice', (req, res) => {
  let ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress
  if (ip.substr(0, 7) == "::ffff:") {
    ip = ip.substr(7)
  }
  if (state.redisClient.hget("devices", req.query.id)) {
    state.redisClient.send_command("hdel", ["devices", req.query.id], () => {
      state.redisClient.hset("devices", req.query.id, ip, redis.print)
    })
  }
  else {
    state.redisClient.hset("devices", req.query.id, ip, redis.print)
  }

  res.end(ip)
})

app.get('/getdevices', (req, res) => {
  state.redisClient.hgetall("devices", (err, devices) => {
    response = devices ? devices : {"error": "list is empty"}
    res.end(JSON.stringify(response))
  })
})

app.get('/setsequence', (req, res) => {
  let sequence = req.query.sequence
  setSequence(state, sequence)

  res.end('OK')
})



/* SERVER INIT */
const server = app.listen(8081, () => {
  const host = server.address().address
  const port = server.address().port
  console.log("Listening at http://%s:%s", host, port)
})

/* REMOTE CONTROLLER INIT */
usb.on('attach', remoteControllerInit.bind(null, usb, state))
usb.on('detach', _=>{})

remoteControllerInit(usb, state)

setSequence(state, config.defaultSequence)

process()

