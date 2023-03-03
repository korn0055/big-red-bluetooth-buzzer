import asyncio
import board
import digitalio
import keypad
import neopixel
import time
import supervisor
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.pulse import Pulse
# from adafruit_led_animation.animation.sparkle import Sparkle
# from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.color import PURPLE, JADE, AMBER, RED, GREEN, WHITE, BLUE
import ble_comms
import microcontroller

_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

def ticks_add(ticks, delta):
    "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (ticks + delta) % _TICKS_PERIOD

def ticks_diff(ticks1, ticks2):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff

def ticks_less(ticks1, ticks2):
    "Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks"
    return ticks_diff(ticks1, ticks2) < 0

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=1.0, auto_write=False)

# button_a_pin = digitalio.DigitalInOut(board.D4)
# button_a_pin.switch_to_input(pull=digitalio.Pull.DOWN)
# button_a = Debouncer(button_a_pin)

MULTI_PRESS_TIMEOUT_MS = 500 #
LONGPRESS_THRESHOLD_MS = 5000 #

class Signals:
    def __init__(self):
        self.button_a_state = False
        self.button_a_timestamp = time.monotonic()
        self.button_a_multipress_count = 0
        self.button_a_longpress_detected = False

class ButtonEvent:
    pass

class ButtonPressedEvent(ButtonEvent):
    pass

class ButtonHoldEvent(ButtonEvent):
    pass

class ButtonMultiPressEvent(ButtonEvent):
    def __init__(self, count):
        super().__init__()
        self.count = count

class ButtonReleasedEvent(ButtonEvent):
    pass

async def catch_pin_transitions(pin, signals : Signals, event_queue):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        hold_check_time = None
        print('start key task')
        state = False
        prev_event = None
        hold_start_ticks = None # fire hold event this ms after button is pressed
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    signals.button_a_state = True
                    signals.button_a_press_timestamp = event.timestamp
                    signals.button_a_longpress_detected = False

                    unpressed_duration = event.timestamp - (prev_event.timestamp if prev_event else supervisor.ticks_ms())
                    if ticks_less(unpressed_duration, MULTI_PRESS_TIMEOUT_MS):
                        signals.button_a_multipress_count += 1
                        if signals.button_a_multipress_count > 1:
                            event_queue.put(ButtonMultiPressEvent(signals.button_a_multipress_count))
                    else:
                        signals.button_a_multipress_count = 0
                    hold_start_ticks = ticks_add(event.timestamp, LONGPRESS_THRESHOLD_MS)
#                     print(f"button pressed after {unpressed_duration} ms (multi press count = {signals.button_a_multipress_count})")
#                     print(f"timestamp={event.timestamp}, hold_start_ticks={hold_start_ticks}, now={supervisor.ticks_ms()}")
                    event_queue.put(ButtonPressedEvent())

                elif event.released:
                    pressed_duration = event.timestamp - signals.button_a_press_timestamp
                    signals.button_a_state = False
                    event_queue.put(ButtonReleasedEvent())
                    hold_start_ticks = None
                    print(f"button released after {pressed_duration} ms (long press = {signals.button_a_longpress_detected})")
                prev_event = event
            if hold_start_ticks and ticks_less(hold_start_ticks, supervisor.ticks_ms()):
                assert prev_event.pressed
                event_queue.put(ButtonHoldEvent())
                hold_start_ticks = None

            await asyncio.sleep(0)
        print('end key task')

async def blink_pixel(index, interval, count):
    for _ in range(count):
        pixels[index] = PURPLE
        await asyncio.sleep(interval)  # Don't forget the "await"!
        pixels[index] = RED
        await asyncio.sleep(interval)  # Don't forget the "await"!

async def blink_led(pin, interval, count, signals):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            mult = 0.5 if signals.button_a_state else 1
            led.value = True
            await asyncio.sleep(interval*mult)  # Don't forget the "await"!
            led.value = False
            await asyncio.sleep(interval*mult)  # Don't forget the "await"!

async def animate_async(animation_obj, duration=0):
#     print(f"start {duration} second animiation")
    end_time = time.monotonic() + duration
    while True if duration == 0 else time.monotonic() < end_time:
        animation_obj.animate()
        await asyncio.sleep(0)

class Controller():
    def __init__(self):
        self.ble = ble_comms.BleComms(self.handle_ble_connection_changed, self.handle_ble_rx)
        self.ble_task = self.ble.run_async()
        self.pixels_task = None
        self.is_ble_connected = False
        self.prev_state = (None, None)
        self.reset()

    def reset(self):
        print("controller reset")
        self.latch_state = False
        self.rank = None
        self.refresh_state()

    #circuitpython asyncio does not support queues :-(
    def put(self, event):
        print(f"event received:{type(event)}")
        if isinstance(event, ButtonPressedEvent):
            self.handle_button_pressed(event)
        elif isinstance(event, ButtonHoldEvent):
            self.handle_button_hold(event)
        elif isinstance(event, ButtonMultiPressEvent):
            self.handle_button_multi_press(event)

    def update_animation(self, animation_obj, *, brightness=None, duration=0):
        print(f"update animation")
        if self.pixels_task:
#             print("cancelling")
            self.pixels_task.cancel()

        if brightness:
#             print("brightness update")
            pixels.brightness = brightness

        if animation_obj:
#             print("new task")
            self.pixels_task = asyncio.create_task(animate_async(animation_obj, duration=duration))
        else:
#             print("off")
            pixels.fill((0, 0, 0))
            pixels.show()

    def handle_button_pressed(self, event):
        self.ble.tx('BOOM')
        if not self.latch_state:
            self.latch_state = True
            self.refresh_state()

    def handle_button_hold(self, event):
        self.ble.tx('RESET')
#         self.update_animation(Comet(pixels, speed=0.05, color=JADE, tail_length=3), brightness=1.0, duration=3.0)
        self.reset()

    def handle_button_released(self, event):
        pass

    def handle_button_multi_press(self, event):
        print(f"MULTI BUTTON PRESS HANDLER count={event.count}")
        if event.count == 10:
            print("!!RESETTING DEVICE!!")
            microcontroller.reset()

    def handle_ble_connection_changed(self, is_connected):
        self.is_ble_connected = is_connected
        self.refresh_state()

    def handle_ble_rx(self, rx_str):
        print(f"rx_str={rx_str} (len={len(rx_str)})")
        if 'RANK' in rx_str:
            self.rank = int(rx_str[4])
            print(f"assigned rank {self.rank}")
            self.refresh_state()
        elif 'RESET' in rx_str:
            self.reset()

    def refresh_state(self, force_update=False):
        state = (self.latch_state, self.is_ble_connected)
        if state == self.prev_state and not force_update:
            print("no change")
        elif state == (False, False):
            self.update_animation(Solid(pixels, color=PURPLE), brightness=0.1)
        elif state == (True, False) or state == (True, True):
            if self.rank:
                self.update_animation(Pulse(pixels, speed=0.05, color=WHITE, period=0.5*self.rank), brightness=1.0)
            else:
                self.update_animation(Pulse(pixels, speed=0.05, color=AMBER, period=1), brightness=1.0)
#                 self.update_animation(Solid(pixels, color=WHITE), brightness=1.0)
#             self.leds_task = asyncio.create_task(animate_async(Pulse(pixels, speed=0.05, color=WHITE, period=1)))
#             self.leds_task = asyncio.create_task(animate_async(ColorCycle(pixels, speed=0.5, colors=(RED, GREEN))))
        elif state == (False, True):
            self.update_animation(Solid(pixels, color=BLUE), brightness=0.1)
        prev_state = state

    async def run(self):
        # not sure if awaiting pixels_tasks works here since the underlying object is changed during execution
        await asyncio.gather(self.pixels_task, self.ble_task)
        # blink = Blink(pixels, speed=0.5, color=RED)
#         self.leds_task = asyncio.create_task(animate_async(blink, 3))
#         await asyncio.gather(self.blink_task)

async def main():

    signals = Signals()
    controller = Controller()
    led1_task = asyncio.create_task(blink_led(board.D13, .25, 100, signals))
    keypad_task = asyncio.create_task(catch_pin_transitions(board.TX, signals, controller))
    controller_task = asyncio.create_task(controller.run())


    await asyncio.gather(led1_task, keypad_task, controller_task)  # Don't forget "await"!
    print("done")

asyncio.run(main())
