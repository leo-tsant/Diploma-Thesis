import paho.mqtt.client as mqtt
import json
import logging
import asyncio
from bleak import BleakScanner, BleakClient
import requests
import time


THINGSBOARD_HOST = "192.168.41.97"
ACCESS_TOKEN = "IbhmKDuzcEIH2MoOtDj0"

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

HUB_NAME = "Pybricks Hub"
headers = {"Content-type": "application/json"}

startProgramFlag = False
stopProgramFlag = False
keepRunningFlag = False
interruptedFlag = False


def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe("v1/devices/me/attributes")
    client.subscribe("v1/devices/me/attributes/response/+")
    client.publish(
        "v1/devices/me/attributes/request/1",
        json.dumps({"clientKeys": "testSwitch"}),
        1,
    )


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    # print(data)
    # global switch_value
    global startProgramFlag
    global stopProgramFlag
    global keepRunningFlag
    global interruptedFlag

    # if msg.topic == "v1/devices/me/attributes/response/1":
    #     if data["client"]["testSwitch"] == "On":
    #         switch_value = "On"
    #     else:
    #         switch_value = "Off"
    #     print("testSwitch: ", switch_value)

    if msg.topic.startswith("v1/devices/me/rpc/request/"):
        if data["method"] == "setSwitchValue":
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"testSwitch": data["params"]}),
                1,
            )
            if data["params"] == True:
                startProgramFlag = True
                keepRunningFlag = True
            else:
                keepRunningFlag = False
                interruptedFlag = True


def hub_filter(device, ad):
    return device.name and device.name.lower() == HUB_NAME.lower()


def handle_disconnect(_):
    print("Hub was disconnected.")


async def main():
    global startProgramFlag
    global stopProgramFlag
    global keepRunningFlag
    global interruptedFlag

    device = await BleakScanner.find_device_by_filter(hub_filter)
    if not device:
        print(
            f"No device found with the name '{HUB_NAME}'. Make sure it's nearby and running the Pybricks code."
        )
        return

    client_bleak = BleakClient(device, disconnected_callback=handle_disconnect)

    # Shorthand for sending some data to the hub.
    async def send(client, data):
        await client.write_gatt_char(rx_char, data)

    try:
        print(f"Connecting to {device.name}...")
        await client_bleak.connect()
        await client_bleak.start_notify(UART_TX_CHAR_UUID, handle_rx)

        nus = client_bleak.services.get_service(UART_SERVICE_UUID)
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)

        print("Connected successfully.")
        time.sleep(1)
        print("Start the program on the hub now with the button.")

        while True:
            await asyncio.sleep(1)  # Keep the event loop running
            await send(client_bleak, b"0")
            # Break out of the loop when received distance is less than or equal to 100
            if startProgramFlag:
                print("Starting program...")
                await send(client_bleak, b"1")
                while keepRunningFlag:
                    await asyncio.sleep(1)
                    print("Running...")
                if interruptedFlag:
                    await send(client_bleak, b"2")
                    await asyncio.sleep(1)
                    interruptedFlag = False
                startProgramFlag = False
                print("exited while loop")

    except OSError as e:
        if "Operation aborted" in str(e):
            print("Hub shut down.")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()  # Print the stack trace for debugging
    finally:
        await client_bleak.disconnect()


buffer = ""


async def handle_rx(_, data: bytearray):
    global buffer
    global keepRunningFlag

    buffer += data.decode()

    # Check if the message is complete.
    # A BLE data packet can carry a maximum payload of 20 bytes in BLE v4.0 that's why we use a buffer to store the data until we receive the complete message
    if buffer.endswith("\n"):
        print(buffer)

        if "Counter:" in buffer:
            counter = int(buffer.split(":")[-1].strip())

        elif "Done!" in buffer:
            keepRunningFlag = False

        buffer = ""


client_mqtt = mqtt.Client()
client_mqtt.on_connect = on_connect
client_mqtt.on_message = on_message
client_mqtt.username_pw_set(ACCESS_TOKEN)
client_mqtt.connect(THINGSBOARD_HOST, 1883, 60)

try:
    client_mqtt.loop_start()
    asyncio.run(main())
except KeyboardInterrupt:
    client_mqtt.disconnect()