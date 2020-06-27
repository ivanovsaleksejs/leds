import { setSequence } from './sequences.js'

import config from './config.json'

/*
 * Initializes remote controller and adds events for buttons
 */
const remoteControllerInit = (usb, state) =>
{
  let remote = false
  remote = usb.findByIds(6790, 29987) //TODO: move to config or some smarter way
  //remote = usb.findByIds(6790, 29987) //TODO: move to config or some smarter way
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
  deviceInterface.endpoints[0].on("data", processRemoteButtons.bind(null, state))
  deviceInterface.endpoints[0].on("error", _ => {}) // Need not to do anything when device is detached as we rerun init once attached back
}

/*
 * Processes remote controller buttons
 */
const processRemoteButtons = (state, dataBuf) =>
{
  let dataArr = Array.prototype.slice.call(new Uint8Array(dataBuf, 0, 8)) // convert buffer to array
  let pressedButton = [dataArr[0], dataArr[3]]

  if (state.prevButton+'' != pressedButton) {

    if (state.buttonTimeout) {
      clearTimeout(state.buttonTimeout)
    }

    state.prevButton = pressedButton
    let [mode, command] = [config.remoteButtons.modes[pressedButton[0]], config.remoteButtons.commands[pressedButton[1]]]
    if (mode == "OFF" || typeof command == "undefined") {
      setSequence(state, "process")
    }
    else {
      setSequence(state, command)
    }

    state.buttonTimeout = setTimeout(_=>{state.prevButton = false}, 1000)
  }
}

export { remoteControllerInit, processRemoteButtons }


