import config from './config.json'

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
    }
    console.log(state.currentSequences)
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
    console.log(state.currentSequences[device])

    let deviceBuffer = new Uint8Array(0)
    for (let zone in state.currentSequences[device].sequenceData) {

      let zoneData = state.currentSequences[device].sequenceData[zone]

      state.currentSequences[device].sequenceData[zone].step++

      if (state.currentSequences[device].sequenceData[zone].step >= zoneData.animations[zoneData.animationNumber].frameCount) {
        state.currentSequences[device].sequenceData[zone].step = 0
        if (zoneData.animationNumber < zoneData.animations.length - 1) {
          state.currentSequences[device].sequenceData[zone].animationNumber++
        }
      }
      if (typeof zoneData.animations[zoneData.animationNumber][zoneData.step] !== "undefined") {
        deviceBuffer = LEDSerialExpander.mergeArrays(deviceBuffer, zoneData.animations[zoneData.animationNumber][zoneData.step])
      }
    }
    let header = LEDSerialExpander.setupHeader(device, deviceBuffer.length)
    deviceBuffer = LEDSerialExpander.mergeArrays(header, deviceBuffer)
    deviceBuffer = LEDSerialExpander.mergeArrays(deviceBuffer, LEDSerialExpander.crcsum(deviceBuffer))

    output = LEDSerialExpander.mergeArrays(output, deviceBuffer)
  }
  output = LEDSerialExpander.mergeArrays(output, LEDSerialExpander.drawall)
  state.serialport.write(output)
}

export { setSequence, processSequences }