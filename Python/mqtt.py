# from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

# telemetry = {"force": 44, "enabled": False, "currentFirmwareVersion": "v1.2.2"}

# # 192.168.41.97 is the IP address of WSL instance
# client = TBDeviceMqttClient("192.168.41.97", 1883, "qg6J2dvtuaHHx8HVNJlx")
# # Connect to ThingsBoard
# client.connect()
# # Sending telemetry without checking the delivery status
# client.send_telemetry(telemetry)
# # Sending telemetry and checking the delivery status (QoS = 1 by default)
# result = client.send_telemetry(telemetry)
# # get is a blocking call that awaits delivery status
# success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
# # Disconnect from ThingsBoard
# client.disconnect()
# from time import sleep
# from tb_device_mqtt import TBDeviceMqttClient


# def callback(result, *args):
#     attribute, value = next(iter(result.items()))
#     print(f"{attribute} changed to {value}")


# client = TBDeviceMqttClient("192.168.41.97", 1883, "qg6J2dvtuaHHx8HVNJlx")
# client.connect()
# client.subscribe_to_all_attributes(callback)
# while True:
#     sleep(1)

import paho.mqtt.client as mqtt
import json
import logging
from time import sleep

from tb_device_mqtt import TBDeviceMqttClient

logging.basicConfig(level=logging.DEBUG)

# Initialize switch_value
switch_value = False


def callback(result, *args):
    print(result, *args)


def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")


def on_message(client, userdata, msg):
    global switch_value
    data = json.loads(msg.payload)
    if data["method"] == "getSwitchValue":
        print("Get switch value request")
        print("Current switch value: ", switch_value)
        client.publish(
            msg.topic.replace("request", "response"),
            json.dumps({"value": switch_value}),
            1,
        )
    elif data["method"] == "setSwitchValue":
        print("Set switch value request")
        switch_value = data["params"]  # assuming the new value is passed in 'params'
        print("New switch value: ", switch_value)


def sub_to_attribute(client):
    client.subscribe_to_attribute("SwitchValue", callback)


client = TBDeviceMqttClient("192.168.41.97", 1883, "qg6J2dvtuaHHx8HVNJlx")
client.on_connect = on_connect
client.on_message = on_message
client.connect()
sub_to_attribute(client)


while True:
    sleep(1)
