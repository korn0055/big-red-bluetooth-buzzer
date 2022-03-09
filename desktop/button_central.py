import asyncio
from bleak import BleakClient


UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


notify_uuid = UART_TX_CHAR_UUID

def callback(sender, data):
    print(sender, data)

async def connect_to_device(address):
    print("starting", address, "loop")
    async with BleakClient(address, timeout=5.0) as client:

        print("connect to", address)
        try:
            await client.start_notify(notify_uuid, callback)
            await asyncio.sleep(10.0)
            await client.stop_notify(notify_uuid)
        except Exception as e:
            print(e)

    print("disconnect from", address)


async def main(addresses):
    return await asyncio.gather(*(connect_to_device(address) for address in addresses))

if __name__ == "__main__":
    one = "C2:BD:72:AF:F5:2C"
    two = "E3:55:A0:1B:BB:0B"
    asyncio.run(
        main(
            [
                one,
                # two,
            ]
        )
    )