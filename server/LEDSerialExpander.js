const toBytesInt32 = num => {
    let arr = new Uint8Array([
        (num & 0xff000000) >> 24,
        (num & 0x00ff0000) >> 16,
        (num & 0x0000ff00) >> 8,
        (num & 0x000000ff)
    ]);
    return arr;
}

const crc_table = [
    0x00000000,
    0x1db71064,
    0x3b6e20c8,
    0x26d930ac,
    0x76dc4190,
    0x6b6b51f4,
    0x4db26158,
    0x5005713c,
    0xedb88320,
    0xf00f9344,
    0xd6d6a3e8,
    0xcb61b38c,
    0x9b64c2b0,
    0x86d3d2d4,
    0xa00ae278,
    0xbdbdf21c
]

const crcsum = b_array => {

    // A lot of >>>0 because JS enforces signed integers and bitwise logic breaks
    let tbl_idx = 0
    let crc = 0xffffffff >>> 0

    for (let b = 0; b < b_array.length; b++) {
        tbl_idx = (crc ^ b_array[b]) >>> 0
        crc = (crc_table[(tbl_idx & 0x0f)>>>0] ^ ((crc >>> 4)>>>0))>>>0
        tbl_idx = (crc ^ ((b_array[b] >>> 4)>>>0))>>>0
        crc = (crc_table[(tbl_idx & 0x0f)>>>0] ^ ((crc >>> 4)>>>0))>>>0
    }

    crc = (crc & 0xffffffff) >>> 0
    crc = crc ^ 0xffffffff

    // Little endian bytes
    return toBytesInt32(crc).reverse()
}

const setupHeader = (channel, length) => {
    let setup = new Uint8Array(10)
    setup[0] = 'U'.charCodeAt(0)
    setup[1] = 'P'.charCodeAt(0)
    setup[2] = 'X'.charCodeAt(0)
    setup[3] = 'L'.charCodeAt(0)

    setup[4] = channel
    setup[5] = 1 // Set up ws2812. Probably must be moved to config
    setup[6] = 3 // Color count, hardcoded for now
    setup[7] = 0b11000 // Color config, hardcoded for now
    // Little endian length
    setup[8] = length % 256
    setup[9] = parseInt(length / 256)

    return setup
}

const mergeArrays = (a, b) => {
    const c = new Uint8Array(a.length + b.length)
    c.set(a)
    c.set(b, a.length)
    return c
}

let drawall = new Uint8Array(6)
drawall[0] = 'U'.charCodeAt(0)
drawall[1] = 'P'.charCodeAt(0)
drawall[2] = 'X'.charCodeAt(0)
drawall[3] = 'L'.charCodeAt(0)

drawall[4] = 0
drawall[5] = 2

drawall = mergeArrays(drawall, crcsum(drawall))

export { drawall, setupHeader, mergeArrays, crcsum }
