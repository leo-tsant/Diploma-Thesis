import requests
import json

url = "http://localhost:8080/api/v1/qg6J2dvtuaHHx8HVNJlx/telemetry"  # replace "ACCESS_TOKEN" with your device's access token
headers = {"Content-type": "application/json"}
data = {"force": 40}

requests.post(url, data=json.dumps(data), headers=headers)
