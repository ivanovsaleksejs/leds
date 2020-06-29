import config from './config.json'

const request = require('request')

const animations = require('./animations')

const LEDSerialExpander = require('./LEDSerialExpander.js')

/*
 * Function that sends a name of sequence to all registered devices
 */
const setSequence = (state, sequence) =>
{
  state.redisClient.hgetall("devices", (err, devices) => {
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
  if (typeof config.uart_devices !== "undefined" && typeof config.sequences[sequence] !== "undefined") {
    for (let device in config.uart_devices) {
      if (typeof state.sequences[device] == "undefined" || typeof state.sequences[device][sequence] == "undefined") {
        if (typeof state.sequences[device] == "undefined") {
          state.sequences[device] = {}
        }
        if (typeof config.sequences[sequence][device] !== "undefined") {
          state.sequences[device][sequence] = prepareSequence(config.uart_devices[device], config.sequences[sequence][device])
        }
      }
      state.currentSequences[device] = {
        sequenceName: sequence,
        sequenceData: state.sequences[device][sequence]
      }
      for (let zone in state.currentSequences[device].sequenceData) {
        state.currentSequences[device].sequenceData[zone].animationNumber = 0
        state.currentSequences[device].sequenceData[zone].step = 0
      }
    }
  }
}

const cacheSequences = (state) => {
  for (let seq in config.sequencesToCache) {
    let sequence = config.sequencesToCache[seq]
    if (typeof config.uart_devices !== "undefined" && typeof config.sequences[sequence] !== "undefined") {
      for (let device in config.uart_devices) {
        if (typeof state.sequences[device] == "undefined" || typeof state.sequences[device][sequence] == "undefined") {
          if (typeof state.sequences[device] == "undefined") {
            state.sequences[device] = {}
          }
          if (typeof config.sequences[sequence][device] !== "undefined") {
            state.sequences[device][sequence] = prepareSequence(config.uart_devices[device], config.sequences[sequence][device])
          }
        }
      }
    }
  }
}

const prepareSequence = (device, sequence) => {
  let ret = []
  for (let zone in sequence) {
    ret[zone] = {
      animationNumber: 0,
      step: 0,
      animations: []
    }
    for (let index in sequence[zone].animation_data.animations) {

      let animation = sequence[zone].animation_data.animations[index]
      let animation_name = animation.animation_name

      if (typeof animations[animation_name] !== "undefined") {
        ret[zone].animations.push(animations[animation_name](sequence[zone], animation))
      }
    }
  }
  return ret
}

const processSequences = (state) => {

  let output = new Uint8Array(0)

  for (let device in state.currentSequences) {

    let deviceBuffer = new Uint8Array(0)
    for (let zone in state.currentSequences[device].sequenceData) {

      let zoneData = state.currentSequences[device].sequenceData[zone]

      if (typeof zoneData.animations[zoneData.animationNumber].animation_data.time !== "undefined") {
        let d = new Date()
        if (typeof zoneData.animations[zoneData.animationNumber].animation_data.startTime == "undefined" || zoneData.animations[zoneData.animationNumber].animation_data.startTime == 0) {
          state.currentSequences[device].sequenceData[zone].animations[zoneData.animationNumber].animation_data.startTime = d.getTime()
        }
        if (d.getTime() - zoneData.animations[zoneData.animationNumber].animation_data.startTime >= zoneData.animations[zoneData.animationNumber].animation_data.time) {
          state.currentSequences[device].sequenceData[zone].animations[zoneData.animationNumber].animation_data.startTime = 0
          if (zoneData.animationNumber < zoneData.animations.length - 1) {
            state.currentSequences[device].sequenceData[zone].animationNumber++
            state.currentSequences[device].sequenceData[zone].step = 0
          }
        }
      }
      if (typeof zoneData.animations[zoneData.animationNumber].animation_data.direction !== "undefined") {
        if (zoneData.animations[zoneData.animationNumber].animation_data.direction == 0) {
          state.currentSequences[device].sequenceData[zone].step++
          if (state.currentSequences[device].sequenceData[zone].step >= zoneData.animations[zoneData.animationNumber].animation_data.frameCount) {
            if (typeof zoneData.animations[zoneData.animationNumber].animation_data.onetime == "undefined") {
              zoneData.animations[zoneData.animationNumber].animation_data.direction = 1
              state.currentSequences[device].sequenceData[zone].step--
            }
            else {
              if (zoneData.animationNumber < zoneData.animations.length - 1) {
                state.currentSequences[device].sequenceData[zone].animationNumber++
              }
            }
          }
        }
        else {
          state.currentSequences[device].sequenceData[zone].step--
          if (state.currentSequences[device].sequenceData[zone].step <= 0) {
            if (typeof zoneData.animations[zoneData.animationNumber].animation_data.onetime == "undefined") {
              zoneData.animations[zoneData.animationNumber].animation_data.direction = 0
            }
            else {
              if (zoneData.animationNumber < zoneData.animations.length - 1) {
                state.currentSequences[device].sequenceData[zone].animationNumber++
              }
            }
          }
        }
      }
      else {
        state.currentSequences[device].sequenceData[zone].step++
        if (state.currentSequences[device].sequenceData[zone].step >= zoneData.animations[zoneData.animationNumber].animation_data.frameCount 
          && typeof zoneData.animations[zoneData.animationNumber].animation_data.time == "undefined") {
          state.currentSequences[device].sequenceData[zone].step = 0
          if (zoneData.animationNumber < zoneData.animations.length - 1) {
            state.currentSequences[device].sequenceData[zone].animationNumber++
          }
        }
      }
      zoneData.step = state.currentSequences[device].sequenceData[zone].step

      if (typeof zoneData.animations[zoneData.animationNumber].animation_data.buffer[zoneData.step] !== "undefined") {
        deviceBuffer = LEDSerialExpander.mergeArrays(deviceBuffer, zoneData.animations[zoneData.animationNumber].animation_data.buffer[zoneData.step])
      }
    }
    let header = LEDSerialExpander.setupHeader(config.uart_devices[device].channel, parseInt(deviceBuffer.length / config.colorsPerPixel))
    deviceBuffer = LEDSerialExpander.mergeArrays(header, deviceBuffer)
    deviceBuffer = LEDSerialExpander.mergeArrays(deviceBuffer, LEDSerialExpander.crcsum(deviceBuffer))

    output = LEDSerialExpander.mergeArrays(output, deviceBuffer)
  }
  output = LEDSerialExpander.mergeArrays(output, LEDSerialExpander.drawall)
  setTimeout(_ => {state.serialport.write(output)}, 1)
}

export { setSequence, processSequences, cacheSequences }
