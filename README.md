# Big Red Bluetooth Buzzers for *The Voice*
Code for 3D printed, bluetooth game show buzzers for playing *The Voice* at home, powered by [Adafruit Circuit Playground Bluefruit](https://www.adafruit.com/product/4333) boards and a laptop.
Find the full story including build instructions in my [blog post](https://spuriousemissions.com/bluetooth-game-show-buzzers) or [check out a quick video of it action on YouTube.](https://youtu.be/s4T4rPzA93A)

## Overview
A PC communicates with all of the buzzers over bluetooth, keeps track what order they buzz in, and plays the [BOOM sound effect](https://www.youtube.com/watch?v=WLAinq9czTU).  Each buzzer has an [Adafruit Circuit Playground Bluefruit](https://www.adafruit.com/product/4333) inside, which tells the PC whenever the button is pressed and updates its lights based on the rank information it receives in response.  This repo contains code for both sides.  Here's a birdseye view of the situation:

![overview](https://github.com/korn0055/big-red-bluetooth-buzzer/blob/main/docs/diagram/overview.png?raw=true)

## Basic Operation
- Power on all of the buzzers
- Run `button_central.py` (on the PC) 
- Wait for the buzzers to connect to the PC (buzzer lights will change to blue)
- When someone buzzes in, the PC will play the BOOM and the buzzer will start flashing white - fastest for 1st place, slowest for last
- Buzzing in more than once will play the BOOM, but won't change the player's rank
- Holding any buzzer for longer than 5 seconds will reset the game (clear the rankings and set all buzzers to solid blue - assuming all devices are connected)
- Hitting Ctrl-C will (hopefully gracefully) end the script and disconnect the buzzers

## Buzzer Lights Decoder Ring
| Color | Bluetooth | Player buzzed in?
| ------------- | ------------- | ---------|
| solid purple  | disconnected  | no |
| solid blue | connected | no |
| pulsing amber | disconnected | yes |
| pulsing white | connected | yes |

See [this](https://learn.adafruit.com/welcome-to-circuitpython/troubleshooting#circuitpython-rgb-status-light-2978455) for other flash patterns used by CircuitPython (you shouldn't see these if everything is loaded and ok).


## Folders
`desktop` python scripts that run on the PC\
`circuitpy` CircuitPython that runs on the Bluefruit\
`docs` documentation artifacts

# Setup

## Circuit Playground Bluefruit (CircuitPython)
1. Follow [these steps to install CircuitPython on each Bluefruit board.](https://learn.adafruit.com/adafruit-circuit-playground-bluefruit/circuitpython)
After that's done, the device should show up as a Mass Storage Device called `CIRCUITPY` when you plug it into your PC.
1. Copy the contents of the `circuitpy/lib` folder in this repo to the `CIRCUITPY/lib` folder on the bluefruit.
1. Copy `ble_comms.py` and `code.py` from the `circuitpy` folder in this repo to the bluefruit's root.
1. Open a [Serial Console](https://learn.adafruit.com/welcome-to-circuitpython/kattni-connecting-to-the-serial-console) and note the BLE MAC address in this message:  `Waiting to connect <Address c2:bd:72:af:f5:2c>` 
1. Disconnect the USB and supply power using a battery.  The LEDs on the Bluefruit should be solid amber or blue, depending if there's a bluetooth connection.

## PC (python)

The python script uses [bleak](https://github.com/hbldh/bleak) to manage the bluetooth connections.  I believe it's the only package you'll need to install, but haven't verified this with a fresh install.  If you try it, let me know what you find out!

#### Conda Virtual Environment
There is an export of the Anaconda virtual environment I was using.  It probably includes a lot of extra stuff that you don't actually needed for this to run. But if you want, you can import with [conda](https://anaconda.org/anaconda/conda) like this:\
`conda env create -n ENVNAME --file adafruit.yml` 

### Configuration
Before the buzzers can connect, the hardcoded MAC addresses for the Bluefruit boards must set.\
Update these lines in `desktop/button_central.py` with the MAC address of your bluefruit devices (see earlier section for how to get MAC address):
```
        one = "C2:BD:72:AF:F5:2C"
        two = "E3:55:A0:1B:BB:0B"
        three = "d7:10:63:77:a5:d0"
        four = "c2:df:0c:e4:c0:6c"
```

## Fat (Phat) Bass
That **BOOOOM** as all bass.  For best results, hook the PC up to a system with at least 20" subwoofers and [crank it to 11](https://www.youtube.com/watch?v=KOO5S4vxi0o).

# Troubleshooting
- It seems some bluetooth adapters can't run all four simultaneous connections smoothly.  Try connecting just one buzzer at a time (comment out the rest in `button_central.py`) and disconnect other unrelated bluetooth devices.
- Killing the PC app with Ctrl-C *usually* works, but sometimes the bluetooth can get in a weird state.  Try rebooting the terminal, the PC, the Bluefruit boards, etc...
- See general [CircuitPython troubleshooting](https://learn.adafruit.com/welcome-to-circuitpython/troubleshooting)

# Known Issues
- Let's just say this project was hacked together for scream-a-long karaoke at a yearly weekend cabin trip.  Use at your own risk.







