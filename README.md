# Big Red Bluetooth Buzzer for The Voice
Code for 3D printed, bluetooth game show buzzers for playing The Voice at home, powered by Adafruit Circuit Playground Bluefruit boards and a laptop.
Find the full story including build instructions in my [blog post](https://spuriousemissions.com/bluetooth-game-show-buzzers).

# Overview
This repo contains code both for the Adafruit Circuit Playground Bluefruit inside each buzzer, as well as the the application that runs on the PC which communicates with all of the buzzers and plays the sound effects.

![overview](https://github.com/korn0055/big-red-bluetooth-buzzer/blob/main/docs/diagram/overview.png?raw=true)

## Folders
`desktop` python scripts that run on the PC\
`circuitpy` circuitpython that runs on the Bluefruit\
`docs` documentation artifacts

## Ciruit Playground Bluefruit 
### Setup
1. Follow [these steps to install CircuitPython on each Bluefruit board.](https://learn.adafruit.com/adafruit-circuit-playground-bluefruit/circuitpython)
After that's done, the device should show up as Mass Storage Device called `CIRCUITPY` when you plug it into your PC.\
1. Copy the contents of `circuitpy/lib` to `CIRCUITPY/lib`
1. From the `circuitpy` folder in this repo, copy `ble_comms.py` and `code.py` to the bluefruit's root.
1. Disconnect the USB and power batteries.
### LED Colors
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |


## PC Software

### Dependencies
#### Conda Virtual Environment
Import a new [conda](https://anaconda.org/anaconda/conda) environment from the `desktop` folder\
`conda env create -n ENVNAME --file adafruit.yml` 

### Configuring



### Running




