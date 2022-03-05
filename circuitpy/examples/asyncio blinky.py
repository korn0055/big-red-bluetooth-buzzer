import asyncio
import board
import digitalio
import keypad
import neopixel
import time

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10)

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

# button_a_pin = digitalio.DigitalInOut(board.D4)
# button_a_pin.switch_to_input(pull=digitalio.Pull.DOWN)
# button_a = Debouncer(button_a_pin)

MULTI_PRESS_TIMEOUT = 0.5 # 
LONGPRESS_THRESHOLD = 2 #

class Signals:
    def __init__(self):
        self.button_a_state = False
        self.button_a_timestamp = time.monotonic()
        self.button_a_multipress_count = 0
        self.button_a_longpress_detected = False

async def catch_pin_transitions(pin, signals : Signals):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        print('start keys')
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    unpressed_duration = time.monotonic() - signals.button_a_timestamp
                    signals.button_a_state = True
                    signals.button_a_timestamp = time.monotonic()
                    signals.button_a_longpress_detected = False
                    if unpressed_duration < MULTI_PRESS_TIMEOUT:
                        signals.button_a_multipress_count += 1
                    else:
                        signals.button_a_multipress_count = 0
                    print(f"button pressed after {unpressed_duration} seconds (multi press count = {signals.button_a_multipress_count})")
                elif event.released:
                    pressed_duration = time.monotonic() - signals.button_a_timestamp
                    signals.button_a_state = False
                    signals.button_a_timestamp = time.monotonic()
                    signals.button_a_longpress_detected = pressed_duration > LONGPRESS_THRESHOLD
                    print(f"button release after {pressed_duration} seconds (long press = {signals.button_a_longpress_detected})")
                        
            await asyncio.sleep(0)

async def blink_pixel(index, interval, count):
    for _ in range(count):
        pixels[index] = PURPLE
        await asyncio.sleep(interval)  # Don't forget the "await"!
        pixels[index] = YELLOW
        await asyncio.sleep(interval)  # Don't forget the "await"!

async def blink(pin, interval, count, signals):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            mult = 0.5 if signals.button_a_state else 1
            led.value = True
            await asyncio.sleep(interval*mult)  # Don't forget the "await"!
            led.value = False
            await asyncio.sleep(interval*mult)  # Don't forget the "await"!


async def main():
    signals = Signals()
    print(signals.button_a_state)
    led1_task = asyncio.create_task(blink(board.D13, .25, 100, signals))
    led2_task = asyncio.create_task(blink_pixel(0, 1.0, 20))
    await(asyncio.sleep(0.1))
    led2_task = asyncio.create_task(blink_pixel(1, 1.0, 20))
    await(asyncio.sleep(0.1))
    led2_task = asyncio.create_task(blink_pixel(2, 1.0, 20))
    await(asyncio.sleep(0.1))
    led2_task = asyncio.create_task(blink_pixel(3, 1.0, 20))
    led2_task = asyncio.create_task(blink_pixel(4, 1.0, 20))
    keypad_task = asyncio.create_task(catch_pin_transitions(board.TX, signals))

    await asyncio.gather(led1_task, led1_task, keypad_task)  # Don't forget "await"!
    print("done")


asyncio.run(main())
