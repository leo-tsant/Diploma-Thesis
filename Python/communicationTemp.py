import paho.mqtt.client as mqtt
import json
import asyncio
from bleak import BleakScanner, BleakClient
from contextlib import suppress
import requests
import time
import serial
import re
import struct
import keyboard

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

HUB_NAME = "Pybricks Hub"

# Establish serial connection
arduino_port = "COM9"  # Replace with your Arduino's COM port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)


async def main():
    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

    # Do a Bluetooth scan to find the hub.
    device = await BleakScanner.find_device_by_name(HUB_NAME)

    if not device:
        print(
            f"No device found with the name '{HUB_NAME}'. Make sure it's nearby and running the Pybricks code."
        )
        return

    # Connect to the hub
    async with BleakClient(device, handle_disconnect) as client:
        # Subscribe to notifications from the hub.
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        print("Connected to the hub.")

        # Shorthand for sending some data to the hub.
        async def send(data):
            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data,  # prepend "write stdin" command (0x06)
                response=True,
            )

        try:
            print("Start the program on the hub now with the button.")

            while True:
                # Get weight value from Arduino
                if ser.in_waiting > 0:  # Check if data is available
                    weight_str = (
                        ser.readline().decode().strip()
                    )  # Read, decode, and remove whitespace
                    weight = float(re.findall(r"\d+\.\d+", weight_str)[0])
                    data_to_send_2 = struct.pack("!f", weight)
                    print(f"Weight: {weight}")
                if keyboard.is_pressed("g"):
                    await send(data_to_send_2)
                    await asyncio.sleep(1)

        except OSError as e:
            if "Operation aborted" in str(e):
                print("Hub shut down.")
            else:
                print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()  # Print the stack trace for debugging


buffer = ""


async def handle_rx(_, data: bytearray):
    global buffer

    buffer += data.replace(b"\x00", b"").decode()

    # Check if the message is complete.
    # A BLE data packet can carry a maximum payload of 20 bytes in BLE v4.0 that's why we use a buffer to store the data until we receive the complete message
    if buffer.endswith("\n"):
        if "@" in buffer:
            buffer = buffer.replace("@", "")
        print(buffer)
        buffer = ""


# Run the main async program.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
