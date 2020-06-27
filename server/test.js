const SerialPort = require('serialport')
const port = new SerialPort('/dev/ttyS0', {
    baudRate: 2304000
})

const toBytesInt32 = (num) => {
    arr = new Uint8Array([
     (num & 0xff000000) >> 24,
     (num & 0x00ff0000) >> 16,
     (num & 0x0000ff00) >> 8,
     (num & 0x000000ff)
	]);
    return arr;
}

const crc_table = [0x00000000, 0x1db71064, 0x3b6e20c8, 0x26d930ac, 0x76dc4190, 0x6b6b51f4, 0x4db26158, 0x5005713c,
	            0xedb88320, 0xf00f9344, 0xd6d6a3e8, 0xcb61b38c, 0x9b64c2b0, 0x86d3d2d4, 0xa00ae278, 0xbdbdf21c]
const crcsum = (b_array) => {
        
    table_idx = 0
    crc = 0xffffffff >>> 0
    for (b = 0; b < b_array.length; b++) {
        tbl_idx = (crc ^ b_array[b]) >>> 0
        crc = (crc_table[(tbl_idx & 0x0f)>>>0] ^ ((crc >>> 4)>>>0))>>>0
        tbl_idx = (crc ^ ((b_array[b] >>> 4)>>>0))>>>0
        crc = (crc_table[(tbl_idx & 0x0f)>>>0] ^ ((crc >>> 4)>>>0))>>>0
    }
    crc = (crc & 0xffffffff) >>> 0
    crc = crc ^0xffffffff
        
    return toBytesInt32(crc).reverse()
}

const mergeArrays = (a, b) => {
    const c = new Uint8Array(a.length + b.length)
    c.set(a)
    c.set(b, a.length)
    return c
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

let drawall = new Uint8Array(6)
drawall[0] = 'U'.charCodeAt(0)
drawall[1] = 'P'.charCodeAt(0)
drawall[2] = 'X'.charCodeAt(0)
drawall[3] = 'L'.charCodeAt(0)

drawall[4] = 0
drawall[5] = 2

const headers = []

const setup = new Uint8Array(10)
setup[0] = 'U'.charCodeAt(0)
setup[1] = 'P'.charCodeAt(0)
setup[2] = 'X'.charCodeAt(0)
setup[3] = 'L'.charCodeAt(0)

setup[4] = 0
setup[5] = 1
setup[6] = 3
setup[7] = 0b11000
setup[8] = 148
setup[9] = 2

headers[0] = [...setup]
headers[1] = [...setup]
headers[1][4] = 1
headers[1][8] = 88


const doAnimation = async () => {
const buffer1 = new Uint8Array(660*3)
for (let i = 0; i < buffer1.length; i++) {
    buffer1[i] = 0x7F
}
const buffer2 = new Uint8Array(660*3)
for (let i = 0; i < buffer2.length; i++) {
    buffer2[i] = 0x00
}
const buffer3 = new Uint8Array(600*3)
for (let i = 0; i < buffer3.length; i++) {
    buffer3[i] = 0x7F
}
const buffer4 = new Uint8Array(600*3)
for (let i = 0; i < buffer4.length; i++) {
    buffer4[i] = 0x00
}
const data1 = mergeArrays(headers[0], buffer1)
const send1 = mergeArrays(data1, crcsum(data1))
const data2 = mergeArrays(headers[0], buffer2)
const send2 = mergeArrays(data2, crcsum(data2))
const data3 = mergeArrays(headers[1], buffer3)
const send3 = mergeArrays(data3, crcsum(data3))
const data4 = mergeArrays(headers[1], buffer4)
const send4 = mergeArrays(data4, crcsum(data4))

let batch1 = mergeArrays(send1, send3)
let batch2 = mergeArrays(send2, send4)

drawall = mergeArrays(drawall, crcsum(drawall))

batch1 = mergeArrays(batch1, drawall)
batch2 = mergeArrays(batch2, drawall)

k=0
let a = new Date()
let start = 0
let end = 0
let diff = 0
while (true) {
	start = a.getTime()		
	setTimeout((data => _ => {port.write(data)})(k%2 == 0 ? batch1 : batch2), 1)

	k++
	a = new Date()
	end = a.getTime()
	diff = end - start
	await sleep(Math.min(diff, 30))

}
}

doAnimation()
