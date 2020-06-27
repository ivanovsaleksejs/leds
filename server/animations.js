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
    animation.animation_data.buffer = [[]]
    animation.animation_data.frameCount = 1

    return animation
}

const flicker = (zone,  animation) => {

    animation.animation_data.buffer = [[]]
    animation.animation_data.frameCount = 1

    return animation
}

const solid = (zone, animation) => {

    animation.animation_data.buffer = []
    animation.animation_data.buffer[0] = new Uint8Array(zone.animation_data.zoneLength * zone.animation_data.stripLength * config.colorsPerPixel)
    let color = 0

    for (let c in animation.animation_data.color) {
        color = animation.animation_data.color[c]
        animation.animation_data.buffer[0] = animation.animation_data.buffer.map((x, i) => i % config.colorsPerPixel == c ? color : x)
    }

    animation.animation_data.frameCount = 1

    return animation
}

export { fade, blink, flicker, solid }
