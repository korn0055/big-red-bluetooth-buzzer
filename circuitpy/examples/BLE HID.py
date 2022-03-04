# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example acts as a BLE HID keyboard to peer devices.
Attach five buttons with pullup resistors to Feather nRF52840
  each button will send a configurable keycode to mobile device or computer
"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

button_1_pin = DigitalInOut(board.D4)
button_1_pin.switch_to_input(pull=Pull.DOWN)
button_1 = Debouncer(button_1_pin)

button_2_pin = DigitalInOut(board.D5)
button_2_pin.switch_to_input(pull=Pull.DOWN)
button_2 = Debouncer(button_2_pin)

hid = HIDService()

device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                manufacturer="Adafruit Industries")
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "CircuitPython HID"

ble = adafruit_ble.BLERadio()
if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)
while True:
    while not ble.connected:
        pass
    print("Start typing:")

    while ble.connected:
        button_1.update()
        button_2.update()
        if button_1.rose:  # pull up logic means button low when pressed
            k.send(Keycode.BACKSPACE)
            print("back")  # for debug in REPL
            k.send(205)
            time.sleep(0.01)

        if button_2.rose:
            kl.write("Bluefruit")  # use keyboard_layout for words
#             k.send(Keyboard.X)
            print("Bluefruit")
            time.sleep(0.01)

        time.sleep(0.01)


    ble.start_advertising(advertisement)
