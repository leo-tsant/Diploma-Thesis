import requests

url = "http://localhost:8080/api/plugins/telemetry/DEVICE/636a9710-5edc-11ee-a2c1-632021637dca/timeseries/delete?keys=hubButtonColor&deleteAllDataForKeys=true"
headers = {
    "Content-Type": "application/json",
    "X-Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0ZW5hbnRAdGhpbmdzYm9hcmQub3JnIiwidXNlcklkIjoiMmE5YjE1NTAtNWVjYy0xMWVlLThhZGYtMDU3NmNjNjNiMWJlIiwic2NvcGVzIjpbIlRFTkFOVF9BRE1JTiJdLCJzZXNzaW9uSWQiOiJiNWU3Njg1Mi1lNzBkLTQ2OTYtYWM4OS00NjhjYTkzMTE5MzQiLCJpc3MiOiJ0aGluZ3Nib2FyZC5pbyIsImlhdCI6MTcwODc4NzkwMCwiZXhwIjoxNzA4Nzk2OTAwLCJlbmFibGVkIjp0cnVlLCJpc1B1YmxpYyI6ZmFsc2UsInRlbmFudElkIjoiMmE0NTU0MzAtNWVjYy0xMWVlLThhZGYtMDU3NmNjNjNiMWJlIiwiY3VzdG9tZXJJZCI6IjEzODE0MDAwLTFkZDItMTFiMi04MDgwLTgwODA4MDgwODA4MCJ9.nilEI1NkHPX2aZLVlxX0EnILK2mO0KORz2JXNKUXDuHqKgNr3iWF4MEuhB1kpwsJavOS9n-tCG2Sy9bfmy2KCQ",
}

response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print("Telemetry key deleted successfully")
else:
    print("Error:", response.text)
