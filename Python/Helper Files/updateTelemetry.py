import requests
import json

url = "http://localhost:8080/api/v1/BpaiwUlHVdQ1BxcUnsJu/telemetry"  # replace "ACCESS_TOKEN" with your device's access token
headers = {"Content-type": "application/json"}
data = {
    # "Green": "0",
    # "Blue": "0",
    # "White": "0",
    # "numberOfBalls": "0",
    # "ballColor": "None",
    # "motorSpeed": "700",
    "energyExpenditure": "0",
}

requests.post(url, data=json.dumps(data), headers=headers)
