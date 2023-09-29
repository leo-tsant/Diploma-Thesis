import paho.mqtt.client as mqtt
import json
import asyncio
from bleak import BleakScanner, BleakClient
import requests
import time


class BallLifterHub:
    def __init__(self):
        self.THINGSBOARD_HOST = "192.168.41.97"
        self.ACCESS_TOKEN = "BpaiwUlHVdQ1BxcUnsJu"
        self.ballLifterURL = (
            f"http://localhost:8080/api/v1/{self.ACCESS_TOKEN}/telemetry"
        )

        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        self.HUB_NAME = "Pybricks Hub"

        self.headers = {"Content-type": "application/json"}

        self.startProgramFlag = False
        self.keepRunningFlag = False
        self.interruptedFlag = False
        self.numberOfBalls = 0
        self.buffer = ""

        self.client_mqtt = mqtt.Client()
        self.client_bleak = None
        self.rx_char = None

        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.username_pw_set(self.ACCESS_TOKEN)
        self.client_mqtt.connect(self.THINGSBOARD_HOST, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("v1/devices/me/rpc/request/+")
        client.subscribe("v1/devices/me/attributes")

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)

        if msg.topic.startswith("v1/devices/me/rpc/request/"):
            method = data.get("method", "")
            params = data.get("params", "")

            if method == "setSwitchValue":
                client.publish(
                    "v1/devices/me/attributes", json.dumps({"switch": params}), 1
                )
                if params:
                    self.startProgramFlag = True
                    self.keepRunningFlag = True
                else:
                    self.keepRunningFlag = False
                    self.interruptedFlag = True
            elif method == "setNumberOfBallsToFetch":
                client.publish(
                    "v1/devices/me/attributes",
                    json.dumps({"numberOfBallsToFetch": params}),
                    1,
                )
                self.numberOfBalls = params

        elif msg.topic == "v1/devices/me/attributes":
            sh_switch = data.get("sh_switch", False)
            if not sh_switch:
                client.publish(
                    "v1/devices/me/attributes", json.dumps({"switch": False}), 1
                )
                self.keepRunningFlag = False
                self.interruptedFlag = True

    async def send(self, data):
        await self.client_bleak.write_gatt_char(self.rx_char, data)

    async def main(self):
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and d.name.lower() == self.HUB_NAME.lower()
        )

        if not device:
            print(
                f"No device found with the name '{self.HUB_NAME}'. Make sure it's nearby and running the Pybricks code."
            )
            return

        self.client_bleak = BleakClient(
            device, disconnected_callback=self.handle_disconnect
        )

        try:
            print(f"Connecting to {device.name}...")
            await self.client_bleak.connect()
            await self.client_bleak.start_notify(self.UART_TX_CHAR_UUID, self.handle_rx)

            nus = self.client_bleak.services.get_service(self.UART_SERVICE_UUID)
            self.rx_char = nus.get_characteristic(self.UART_RX_CHAR_UUID)

            print("Connected successfully.")
            time.sleep(1)
            print("Start the program on the hub now with the button.")

            while True:
                await asyncio.sleep(1)
                if self.startProgramFlag:
                    print("Starting program...")
                    data_to_send = self.numberOfBalls.to_bytes(2, "big")
                    await self.send(data_to_send)
                    while self.keepRunningFlag:
                        await asyncio.sleep(1)
                        print("Running...")
                    if self.interruptedFlag:
                        await asyncio.sleep(1)
                        await self.send(b"st")
                        await asyncio.sleep(1)
                        self.interruptedFlag = False
                    self.startProgramFlag = False
                    self.client_mqtt.publish(
                        "v1/devices/me/attributes", json.dumps({"switch": False}), 1
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

            traceback.print_exc()
        finally:
            await self.client_bleak.disconnect()

    async def handle_rx(self, _, data: bytearray):
        self.buffer += data.decode()

        if self.buffer.endswith("\n"):
            print(self.buffer)
            if "Balls Counter:" in self.buffer:
                ballsCounter = int(self.buffer.split(":")[-1].strip())
                dataToSend = {"numberOfBalls": ballsCounter}
                requests.post(
                    self.ballLifterURL,
                    data=json.dumps(dataToSend),
                    headers=self.headers,
                )
            elif "Counter:" in self.buffer:
                counter = int(self.buffer.split(":")[-1].strip())
            elif "Hub Button Color:" in self.buffer:
                color = self.buffer.split(":")[-1].strip()
                dataToSend = {"hubButtonColor": color}
                requests.post(
                    self.ballLifterURL,
                    data=json.dumps(dataToSend),
                    headers=self.headers,
                )
            elif "Done!" in self.buffer:
                self.keepRunningFlag = False

            self.buffer = ""

    def handle_disconnect(self, _):
        print("Hub was disconnected.")


if __name__ == "__main__":
    ballLifterHub = BallLifterHub()
    ballLifterHub.client_mqtt.loop_start()
    asyncio.run(ballLifterHub.main())
