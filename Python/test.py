import paho.mqtt.client as mqtt
import json
import logging

logging.basicConfig(level=logging.DEBUG)


THINGSBOARD_HOST = "192.168.41.97"
ACCESS_TOKEN = "1OM3ve7hghFnANFN4Qo9"


def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe("v1/devices/me/attributes")
    client.subscribe("v1/devices/me/attributes/response/+")
    client.publish(
        "v1/devices/me/attributes/request/1",
        json.dumps({"clientKeys": "SwitchValue"}),
        1,
    )


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(data)
    global switch_value

    if msg.topic == "v1/devices/me/attributes/response/1":
        if data["client"]["SwitchValue"] == "On":
            switch_value = "On"
        else:
            switch_value = "Off"
        print("Switch value: ", switch_value)

    if msg.topic.startswith("v1/devices/me/rpc/request/"):
        requestId = msg.topic[len("v1/devices/me/rpc/request/") :]
        print(requestId)
        if data["method"] == "getSwitchValue":
            client.publish(
                msg.topic.replace("request", "response"),
                json.dumps({"value": switch_value}),
                1,
            )
            client.publish(
                "v1/devices/me/attributes/response/1",
                json.dumps({"SwitchValue": switch_value}),
                1,
            )
        elif data["method"] == "setSwitchValue":
            if data["params"] == True:
                switch_value = "On"
            else:
                switch_value = "Off"
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"SwitchValue": switch_value}),
                1,
            )


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)


try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
