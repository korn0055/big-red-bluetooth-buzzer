import asyncio
from http import client
from bleak import BleakClient
import audio

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

notify_uuid = UART_TX_CHAR_UUID
SIGNAL_SHUTDOWN = False

class Button():
    def __init__(self, address, controller):
        self.address = address
        self.client = BleakClient(address)
        self.controller = controller
        self.rank = None
        self.client.set_disconnected_callback(self.disconnect_callback)

    def disconnect_callback(self, client):
        print(f"client={client} disconnected")
        assert client is self.client

    async def callback(self, sender, data):
        print(f"client={self.client}, data={data}")
        if b'boom' in data:
            await audio.play_voice_clip()
            self.pressed = True
            await self.controller.report_press(self)

    async def write(self, data_bytes):
        if self.client is not None:
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, data_bytes)

    async def connect_to_device(self):
        print("starting", self.address, "loop")
        try:
            await self.client.connect()
            print("connected to", self.address)
            await self.client.start_notify(notify_uuid, self.callback)
            # await asyncio.sleep(10.0)
            # await self.client.stop_notify(notify_uuid)
        except Exception as e:
            print(e)
            await self.client.disconnect()

    async def auto_reconnect(self):
        global SIGNAL_SHUTDOWN
        while not SIGNAL_SHUTDOWN:
            if not self.client.is_connected:
                await self.connect_to_device()
            await asyncio.sleep(0)
class CentralController:
    def __init__(self, addresses) -> None:
        self.buttons = [Button(address, controller=self) for address in addresses]
        self.reset_ranking()

    def reset_ranking(self):
        for b in self.buttons:
            b.rank = None
        self.current_rank = 1

    async def report_press(self, button):
        if button.rank is None:
            button.rank = self.current_rank
            self.current_rank += 1

        await button.write(f"RANK{button.rank}".encode('ascii'))

    async def shutdown(self):
        for b in self.buttons:
            await b.client.disconnect()

    async def run(self):
        return await asyncio.gather(*(button.auto_reconnect() for button in self.buttons))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        one = "C2:BD:72:AF:F5:2C"
        two = "E3:55:A0:1B:BB:0B"
        three = "d7:10:63:77:a5:d0"
        four = "c2:df:0c:e4:c0:6c"
        controller = CentralController(
                [
                    one,
                    two,
                    three,
                    four
                ]
            )
        asyncio.run(controller.run())
    except KeyboardInterrupt:
        print("Process interrupted")
        SIGNAL_SHUTDOWN = True
        # tasks = [t for t in asyncio.all_tasks() if t is not
        #     asyncio.current_task()]
        # [task.cancel() for task in tasks]
        print("tasks cancelled")
    finally:
        loop.close()
        print("loop closed")
