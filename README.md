This project aims to control via WiFi several ESP32 devices with LED strips connected to each, using Raspberry Pi as a controller and host for node server and react based UI. It can switch LED strips on and off, change animations etc, all from your phone or PC or remote controller.

## Installation

This guide will assume that you're using a /var/www/leds as a working directory for this project. If this is not the case then make sure to make adjustments in leds.service file and in your web server config.

### ESP32

Download and write a [micropython firmware](http://micropython.org/download#esp32) into ESP32. If you want to be able to use an optimized function neopixel_write_compressed then you need to use [my fork of this firmware](https://github.com/ivanovsaleksejs/micropython). If you use up-to-date fork it will probably have a bug that will make LEDs flicker randomly once WiFi module is on. To avoid this I recommend to build from [v1.9.4-701-g10bddc5c2](https://github.com/micropython/micropython/commit/10bddc5c2). You can download a build [here](http://aleksejs.net/share/firmware_1.9.4.bin).

You can use esptool for flashing:

    esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
    esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware_1.9.4.bin

Your system may identify your ESP32 other than /dev/ttyUSB0. You can use ls /dev/ttyUSB\* before and after connecting ESP32 to find a correct name. You  can use other baud rate than 460800 if you wish.

Create files config.json and stripData.json from examples. Pay attention to controllerHostname parameter in config.json - it must be set the same as your Raspberry Pi local domain. Copy all .py files as well as .json files from esp32 folder onto your ESP32 (you can use ampy, for example):

    ampy -p /dev/ttyUSB0 put config.json

You can use screen to check if everything works:

    screen /dev/ttyUSB0 115200

If you see a repl prompt then ESP32 is connected to WiFi and discovered your Raspberry Pi by local domain.

### Wiring

Connect LED strip to your ESP32. Make sure you have connected signal wire to the right pin (see config.json). Also make sure you have connected ESP32 ground to LED strip ground - otherwise you may face unpredictable behavior. Make sure you have powered your setup well - 5V LEDs like ws2812b require 25mA each when provided a white (0xFFFFFF) color, so, if your strip has 60 LEDs it may require up to 1.6A. It's better to use separate PSU (5V 2A or better) for each strip in this case.

### Raspberry Pi

Install nginx and redis on your RPi. You can use other web server software if you like but nginx is easier to configure and it's faster and stable. Configure avahi daemon (it is installed by default if you use raspbian) to specify a local domain according to esp32/config.json. Configure nginx to redirect all /backend links to 8081 port:

    root /var/www/leds/build
    location /backend {
        rewrite ^/backend/(.*) /$1 break;
        proxy_pass http://$server_addr:8081;
    }

Install build-essential and libudev-dev necessary for usb lib: `apt-get install build-essential libudev-dev`. This will allow you to use usb based remote controller.

Install node and yarn. Run

`yarn`

to install all dependencies.

## Running

### Server
You can start server by running

`yarn server`

Or you can register it as systemd item. Create leds.service from example. Create a symlink to it in /etc/systemd/system and enable it with

`sudo systemctl enable leds`

### ESP32

Connect the power to your ESP32 and LED strips. File main.py should be executed automatically and default sequence will be launched.

### Frontend

Create src/config.json from example. Build an app with

`yarn build`

## Demo

[![](http://img.youtube.com/vi/OgqGnGTNRzs/0.jpg)](http://www.youtube.com/watch?v=OgqGnGTNRzs "")
