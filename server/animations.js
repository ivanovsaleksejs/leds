import config from './config.json'


const fade = (zone, animation) => {
    let startColor = Math.max(animation.from)
    let stopColor = startColor * animation.quot
    let frameCount = config.fps * animation.speed / 1000
    for (let i =  0; i < frameCount; i++) {
        quotient = 2 * startColor / (Math.cos(i * Math.PI / frameCount) * (startColor - stopColor) + startColor + stopColor)
    }
}

const blink = (zone, animation) => {

    if (typeof animation.animation_data.buffer == "undefined") {

        animation.animation_data.buffer = []
        if (typeof animation.animation_data.onetime == "undefined") {
            animation.animation_data.direction = 0
        }
        let animation_time = animation.animation_data.speed

        animation.animation_data.frameCount = parseInt(config.fps * animation_time / 1000)

        let currentColor = animation.animation_data.color
        let startColor = Math.max(...animation.animation_data.color)
        let stopColor = startColor * parseFloat(animation.animation_data.quot)
        for (let f =  0; f < animation.animation_data.frameCount; f++) {
            animation.animation_data.buffer[f] = new Uint8Array(zone.animation_data.zoneLength * zone.animation_data.stripLength * config.colorsPerPixel)
            let quotient = 2 * startColor / (Math.cos(f * Math.PI / animation.animation_data.frameCount) * (startColor - stopColor) + startColor + stopColor)
            let frame = [
                parseInt(currentColor[0] / quotient),
                parseInt(currentColor[1] / quotient),
                parseInt(currentColor[2] / quotient)
            ]
            for (let c in frame) {
                let color = frame[config.colorOrder[c]]
                animation.animation_data.buffer[f] = animation.animation_data.buffer[f].map((x, i) => i % config.colorsPerPixel == c ? color : x)
            }
        }
        if (typeof animation.animation_data.reverseOrder !== "undefined") {
            animation.animation_data.buffer = animation.animation_data.buffer.reverse()
        }

    }

    return animation

}

const flicker = (zone,  animation) => {

    return solid(zone, animation)
}

const solid = (zone, animation) => {

    animation.animation_data.buffer = []
    animation.animation_data.buffer[0] = new Uint8Array(zone.animation_data.zoneLength * zone.animation_data.stripLength * config.colorsPerPixel)
    let color = 0

    for (let c in animation.animation_data.color) {
        color = animation.animation_data.color[config.colorOrder[c]]
        animation.animation_data.buffer[0] = animation.animation_data.buffer[0].map((x, i) => i % config.colorsPerPixel == c ? color : x)
    }

    animation.animation_data.frameCount = 1

    return animation
}

export { fade, blink, flicker, solid }
