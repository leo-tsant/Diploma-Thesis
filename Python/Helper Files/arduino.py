import serial
import time
import re

# Establish serial connection
arduino_port = "COM9"  # Replace with your Arduino's COM port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)

# Main loop to read data
while True:
    if ser.in_waiting > 0:  # Check if data is available
        weight_str = (
            ser.readline().decode().strip()
        )  # Read, decode, and remove whitespace
        weight = float(re.findall(r"\d+\.\d+", weight_str)[0])

        try:
            print("Raw Data: " + str(weight) + " g")
        except ValueError:
            print("Invalid weight data received.")
    time.sleep(0.1)  # Adjust delay as needed
