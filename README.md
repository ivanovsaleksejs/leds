This project aims to control several ESP32 devices with LED strips connected to each via WiFi using Raspberry Pi as a controller.

## Installation

Download and write a [micropython firmware](http://micropython.org/download#esp32) into ESP32. You can use esptool for flashing. Create files config.json and stripData.json from examples. Copy all files from esp32 folder onto your ESP32 (you can use ampy).

Install nginx and redis on your RPi. Configure avahi daemon to specify a local domain according to config.json. Configure nginx to redirect all /backend links to 8081 port:

    root /var/www/leds/build
    location /backend {
        rewrite ^/backend/(.*) /$1 break;
        proxy_pass http://$server_addr:8081;
    }

Install node and yarn. Run 

`yarn`

to install all dependencies.

## Running 

### Server

Create leds.service from example. Create a symlink to it in /etc/systemd/system and enable it with

`sudo systemctl enable leds`

### ESP32

Connect LED data wire to the pin from config file. Connect power.

### frontend

Create src/config.json from example. Build app with 

`yarn build`
