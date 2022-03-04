# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import asyncio
import board
import digitalio
from adafruit_circuitplayground import cp

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

async def blink_red_led(interval, count):
    for _ in range(count):
        cp.red_led = True
        await asyncio.sleep(interval)  # Don't forget the "await"!
        cp.red_led = False
        await asyncio.sleep(interval)  # Don't forget the "await"!

async def blink_pixel(index, interval, count):
    for _ in range(count):
        cp.pixels[index] = PURPLE
        await asyncio.sleep(interval)  # Don't forget the "await"!
        cp.pixels[index] = YELLOW
        await asyncio.sleep(interval)  # Don't forget the "await"!

async def blink(pin, interval, count):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            led.value = True
            await asyncio.sleep(interval)  # Don't forget the "await"!
            led.value = False
            await asyncio.sleep(interval)  # Don't forget the "await"!


async def main():
    led1_task = asyncio.create_task(blink_red_led(.25, 10))
    led2_task = asyncio.create_task(blink_pixel(0, 1.0, 20))

    await asyncio.gather(led1_task, led2_task)  # Don't forget "await"!
    print("done")


asyncio.run(main())
