from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import _bleio
import asyncio


class BleComms:
    def __init__(self, connection_status_callback=None, rx_callback=None):
        self.ble = BLERadio()
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)
        self.connection_status_callback = connection_status_callback
        self.rx_callback = rx_callback

    async def connection_loop(self):
        while True:
            self.ble.start_advertising(self.advertisement)
            print(f"Waiting to connect {_bleio.adapter.address}")
            if self.connection_status_callback:
                self.connection_status_callback(False)
            while not self.ble.connected:
                await asyncio.sleep(0)
            print("Connected")
            if self.connection_status_callback:
                self.connection_status_callback(True)

            i = 0
            while self.ble.connected:
                msg = f"hello {i}"
                self.uart.write(msg)
                print(f"{msg} sent")
                await asyncio.sleep(1)
                i += 1

    async def rx_loop(self):
        while True:
            bytes_available = self.uart.in_waiting
            if self.ble.connected and bytes_available > 0:
                rx_bytes = self.uart.read(bytes_available)
                if self.rx_callback:
                    self.rx_callback(rx_bytes)
            await asyncio.sleep(0)

    async def run_async(self):
        connection_task = asyncio.create_task(self.connection_loop())
        rx_task = asyncio.create_task(self.rx_loop())
        await asyncio.gather(connection_task, rx_task)



    def send_button_press(self):
        if self.ble.connected:
            self.uart.write("boom")
            print("ble 'boom'")
