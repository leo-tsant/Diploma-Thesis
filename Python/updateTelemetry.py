import requests
import json

url = "http://localhost:8080/api/v1/IbhmKDuzcEIH2MoOtDj0/telemetry"  # replace "ACCESS_TOKEN" with your device's access token
headers = {"Content-type": "application/json"}
data = {"switch": "On"}

requests.post(url, data=json.dumps(data), headers=headers)
