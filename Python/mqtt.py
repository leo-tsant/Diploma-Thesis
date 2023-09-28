import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = "192.168.41.97"
ACCESS_TOKEN = "IbhmKDuzcEIH2MoOtDj0"


def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe("v1/devices/me/attributes")
    client.subscribe("v1/devices/me/attributes/response/+")
    # client.publish(
    #     "v1/devices/me/attributes",
    #     json.dumps({"testSwitch": False}),
    #     1,
    # )


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(data)
    # global switch_value
    global sendFlag

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


client_mqtt = mqtt.Client()
client_mqtt.on_connect = on_connect
client_mqtt.on_message = on_message
client_mqtt.username_pw_set(ACCESS_TOKEN)
client_mqtt.connect(THINGSBOARD_HOST, 1883, 60)

try:
    client_mqtt.loop_forever()
except KeyboardInterrupt:
    client_mqtt.disconnect()