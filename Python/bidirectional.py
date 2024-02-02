import paho.mqtt.client as mqtt
import json
import asyncio
from bleak import BleakScanner, BleakClient
from contextlib import suppress
import requests
import time


THINGSBOARD_HOST = "192.168.41.97"
ACCESS_TOKEN = "BpaiwUlHVdQ1BxcUnsJu"
ballLifterURL = "http://localhost:8080/api/v1/BpaiwUlHVdQ1BxcUnsJu/telemetry"

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

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


async def main():
    global startProgramFlag
    global stopProgramFlag
    global keepRunningFlag
    global interruptedFlag
    global client_mqtt
    global numberOfBalls

    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        if not main_task.done():
            main_task.cancel()

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
                await asyncio.sleep(1)  # Keep the event loop running
                if startProgramFlag:
                    print("Starting program...")
                    data_to_send = numberOfBalls.to_bytes(2, "big")
                    await send(data_to_send)
                    while keepRunningFlag:
                        await asyncio.sleep(1)
                        print("Running...")
                    if interruptedFlag:
                        await asyncio.sleep(1)
                        await send(b"st")
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


buffer = ""


async def handle_rx(_, data: bytearray):
    global buffer
    global keepRunningFlag

    buffer += data.replace(b"\x00", b"").decode()

    # Check if the message is complete.
    # A BLE data packet can carry a maximum payload of 20 bytes in BLE v4.0 that's why we use a buffer to store the data until we receive the complete message
    if buffer.endswith("\n"):
        if "@" in buffer:
            print("".join(buffer.split("@")[1:]))  # Keep only message after @
        else:
            print(buffer)
        if "Balls Counter:" in buffer:
            ballsCounter = int(
                buffer.split(":")[-1].strip()
            )  # Keep only the counter value

            dataToSend = {"numberOfBalls": ballsCounter}

            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)
        elif "Ball Color:" in buffer:
            data = buffer.split(".")[-1]
            color = data.replace(
                "\x01", ""
            )  # Removes the \x01 character from the string
            dataToSend = {"ballColor": color}
            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)
        elif "Blue Counter" in buffer:
            blueCounter = int(buffer.split(":")[-1].strip())
            dataToSend = {"Blue": blueCounter}
            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)
        elif "Green Counter" in buffer:
            greenCounter = int(buffer.split(":")[-1].strip())
            dataToSend = {"Green": greenCounter}
            requests.post(ballLifterURL, data=json.dumps(dataToSend), headers=headers)
        elif "White Counter" in buffer:
            whiteCounter = int(buffer.split(":")[-1].strip())
            dataToSend = {"White": whiteCounter}
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
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
except KeyboardInterrupt:
    client_mqtt.disconnect()
