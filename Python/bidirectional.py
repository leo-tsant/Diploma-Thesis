import paho.mqtt.client as mqtt
import json
import logging
import asyncio
from bleak import BleakScanner, BleakClient
import requests
import time


THINGSBOARD_HOST = "192.168.41.97"
ACCESS_TOKEN = "BpaiwUlHVdQ1BxcUnsJu"
ballLifterURL = "http://localhost:8080/api/v1/BpaiwUlHVdQ1BxcUnsJu/telemetry"

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

HUB_NAME = "Pybricks Hub"
headers = {"Content-type": "application/json"}

startProgramFlag = False
stopProgramFlag = False
keepRunningFlag = False
interruptedFlag = False
numberOfBalls = 0


def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe("v1/devices/me/attributes")
    client.subscribe("v1/devices/me/attributes/response/+")
    client.publish(
        "v1/devices/me/attributes/request/1",
        json.dumps({"clientKeys": "switch"}),
        1,
    )


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    global startProgramFlag, stopProgramFlag, keepRunningFlag, interruptedFlag, numberOfBalls

    if msg.topic.startswith("v1/devices/me/rpc/request/"):
        if data["method"] == "setSwitchValue":
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"switch": data["params"]}),
                1,
            )
            if data["params"] == True:
                startProgramFlag = True
                keepRunningFlag = True
            else:
                keepRunningFlag = False
                interruptedFlag = True
        elif data["method"] == "setNumberOfBallsToFetch":
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"numberOfBallsToFetch": data["params"]}),
                1,
            )
            numberOfBalls = data["params"]
    elif msg.topic == "v1/devices/me/attributes":
        if data["sh_switch"] == False:
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"switch": False}),
                1,
            )
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
    global client_mqtt
    global numberOfBalls

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
            if startProgramFlag:
                print("Starting program...")
                data_to_send = numberOfBalls.to_bytes(2, "big")
                await send(client_bleak, data_to_send)
                while keepRunningFlag:
                    await asyncio.sleep(1)
                    print("Running...")
                if interruptedFlag:
                    await asyncio.sleep(1)
                    await send(client_bleak, b"st")
                    await asyncio.sleep(1)
                    interruptedFlag = False
                startProgramFlag = False
                client_mqtt.publish(
                    "v1/devices/me/attributes",
                    json.dumps({"switch": False}),
                    1,
                )
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
        if "Balls Counter:" in buffer:
            ballsCounter = int(
                buffer.split(":")[-1].strip()
            )  # Keep only the distance value

            dataToSend = {"numberOfBalls": ballsCounter}

            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)
        elif "Counter:" in buffer:
            counter = int(buffer.split(":")[-1].strip())
        elif "Hub Button Color:" in buffer:
            color = buffer.split(":")[-1].strip()
            dataToSend = {"hubButtonColor": color}
            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)

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
