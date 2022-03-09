from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import _bleio
import asyncio


class BleComms:
    def __init__(self):
        self.ble = BLERadio()
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)

    async def run_async(self):
        while True:
            self.ble.start_advertising(self.advertisement)
            print(f"Waiting to connect {_bleio.adapter.address}")
            while not self.ble.connected:
                await asyncio.sleep(0)
            print("Connected")
            while self.ble.connected:
                self.uart.write("hello")
                await asyncio.sleep(1)

    def send_button_press(self):
        if self.ble.connected:
            self.uart.write("boom")
            print("ble 'boom'")
