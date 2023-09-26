# Start from here
import asyncio
from bleak import BleakScanner, BleakClient

import requests
import json

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

HUB_NAME = "Pybricks Hub"

distanceSensorURL = "http://localhost:8080/api/v1/nwadhzD6rPrPgTRt59aD/telemetry"
forceSensorURL = "http://localhost:8080/api/v1/qg6J2dvtuaHHx8HVNJlx/telemetry"
headers = {"Content-type": "application/json"}


def hub_filter(device, ad):
    return device.name and device.name.lower() == HUB_NAME.lower()


def handle_disconnect(_):
    print("Hub was disconnected.")


flag = False


async def main():
    device = await BleakScanner.find_device_by_filter(hub_filter)
    if not device:
        print(
            f"No device found with the name '{HUB_NAME}'. Make sure it's nearby and running the Pybricks code."
        )
        return

    client = BleakClient(device, disconnected_callback=handle_disconnect)

    # Shorthand for sending some data to the hub.
    async def send(client, data):
        await client.write_gatt_char(rx_char, data)

    try:
        await client.connect()
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        nus = client.services.get_service(UART_SERVICE_UUID)
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)

        print("Start the program on the hub now with the button.")

        while True:
            await asyncio.sleep(1)  # Keep the event loop running
            # Break out of the loop when received distance is less than or equal to 100
            if flag:
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


buffer = ""


async def handle_rx(_, data: bytearray):
    global buffer
    global flag  # Use the global keyword to modify the global variable

    buffer += data.decode()

    # Check if the message is complete.
    # A BLE data packet can carry a maximum payload of 20 bytes in BLE v4.0 that's why we use a buffer to store the data until we receive the complete message
    if buffer.endswith("\n"):
        print(buffer)

        if "Between Distance:" in buffer:
            distance = int(
                buffer.split(":")[-1].strip()
            )  # Keep only the distance value

            dataToSend = {"distance": distance}

            requests.post(
                distanceSensorURL, data=json.dumps(dataToSend), headers=headers
            )
        elif "Force sensor touched:" in buffer:
            force = float(buffer.split(":")[-1].strip())

            dataToSend = {"force": force}

            requests.post(forceSensorURL, data=json.dumps(dataToSend), headers=headers)

        elif "Counter:" in buffer:
            counter = int(buffer.split(":")[-1].strip())

            if counter == 4:
                flag = True

        buffer = ""


asyncio.run(main())
