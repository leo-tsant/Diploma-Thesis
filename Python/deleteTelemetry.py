import requests

url = "http://localhost:8080/api/plugins/telemetry/DEVICE/636a9710-5edc-11ee-a2c1-632021637dca/timeseries/delete?keys=White&deleteAllDataForKeys=true"
headers = {
    "Content-Type": "application/json",
    "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0ZW5hbnRAdGhpbmdzYm9hcmQub3JnIiwidXNlcklkIjoiMmE5YjE1NTAtNWVjYy0xMWVlLThhZGYtMDU3NmNjNjNiMWJlIiwic2NvcGVzIjpbIlRFTkFOVF9BRE1JTiJdLCJzZXNzaW9uSWQiOiI1MDRhN2QxNC0wMjFiLTQ1YWYtOTI5MS02ODljZTFkMzgwMTIiLCJpc3MiOiJ0aGluZ3Nib2FyZC5pbyIsImlhdCI6MTcxMjk0ODkxMCwiZXhwIjoxNzEyOTU3OTEwLCJlbmFibGVkIjp0cnVlLCJpc1B1YmxpYyI6ZmFsc2UsInRlbmFudElkIjoiMmE0NTU0MzAtNWVjYy0xMWVlLThhZGYtMDU3NmNjNjNiMWJlIiwiY3VzdG9tZXJJZCI6IjEzODE0MDAwLTFkZDItMTFiMi04MDgwLTgwODA4MDgwODA4MCJ9.QvxsFxM2Gztn564TABRtJD92fPDRvW4WZ-HkgThg_7JlsiZ3QLgWQZdDNlrKuOgvzHnkuFyAo5K6Vgf8J7VsOQ",
}

response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print("Telemetry key deleted successfully")
else:
    print("Error:", response.text)
