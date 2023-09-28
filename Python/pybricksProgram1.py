from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from usys import stdin, stdout
from uselect import poll, select


hub = PrimeHub()

colorSensor = ColorSensor(Port.A)
largeMotor = Motor(Port.C)
ballLifterMotor = Motor(Port.D)
ballStopperMotor = Motor(Port.F)


def setMotorAngleShortestPath(motor, target_angle, speed):
    # Get the current angle of the motor
    current_angle = motor.angle()

    # Calculate the difference between the target angle and the current angle
    angle_difference = target_angle - current_angle

    # Adjust the difference to take the shortest path
    if abs(angle_difference) > 180:
        angle_difference -= 360

    # Set the target angle by adding the adjusted difference to the current angle
    target_angle = current_angle + angle_difference

    # Rotate the motor to the target angle
    motor.run_target(speed, target_angle, Stop.HOLD, wait=True)


def setMotorAngleLongestPath(motor, target_angle, speed):
    # Get the current angle of the motor
    current_angle = motor.angle()

    # Calculate the difference between the target angle and the current angle
    angle_difference = target_angle - current_angle

    # Adjust the difference to take the longest path
    if angle_difference > 0:
        angle_difference -= 360

    # Set the target angle by adding the adjusted difference to the current angle
    target_angle = current_angle + angle_difference

    # Rotate the motor to the target angle
    motor.run_target(speed, target_angle, Stop.HOLD, wait=True)


# This is a function that waits for a desired color.
def waitForColor(desired_color):
    # While the color is not the desired color, we keep waiting.
    while colorSensor.color() != desired_color:
        wait(20)


def setLargeMotor(numOfBalls):
    setMotorAngleShortestPath(largeMotor, 0, 300)
    largeMotor.reset_angle(0)
    wait(1000)
    largeMotor.run_target(200, numOfBalls * 30, Stop.HOLD, wait=True)


def moveLargeMotorForInterval(remainingBalls):
    setMotorAngleShortestPath(largeMotor, remainingBalls * 30, 100)


def ballLifterExecution(
    numOfBallsWanted,
    numOfBallsRemaining,
    counter,
    firstIterationFlag,
    colors,
    colorIndex,
):
    hub.display.number(counter)

    # setMotorAngleShortestPath(ballLifterMotor, 140, 300) # These adjustments are made so the ballLifterMotor resets it's position
    # ballLifterMotor.reset_angle(-219)                    # every time the program is executed regardless of its starting position

    keyboard1 = poll()
    keyboard1.register(stdin)

    while not keyboard1.poll(0):
        if firstIterationFlag:
            setLargeMotor(numOfBallsWanted)
            firstIterationFlag = False
        setMotorAngleShortestPath(ballLifterMotor, 310, 200)
        setMotorAngleShortestPath(ballStopperMotor, 0, 200)

        setMotorAngleLongestPath(ballLifterMotor, 35, 300)
        setMotorAngleLongestPath(ballLifterMotor, 320, 400)

        waitForColor(Color.WHITE)
        counter += 1
        numOfBallsRemaining -= 1

        moveLargeMotorForInterval(numOfBallsRemaining)
        current_color_name = colors[colorIndex]
        current_color = color_name_to_pybricks.get(
            current_color_name, Color.WHITE
        )  # Default to white if color is not found
        hub.light.on(current_color)
        colorIndex = (colorIndex + 1) % len(colors)
        hub.display.number(counter)
        stdout.write("Balls Counter: " + str(counter) + "\n")
        wait(100)
        stdout.write("Hub Button Color: " + str(current_color_name) + "\n")
        wait(500)
        if counter == numOfBallsWanted:
            break

    setMotorAngleShortestPath(ballStopperMotor, 310, 200)


hub.light.on(Color.CYAN)
color_name_to_pybricks = {
    "RED": Color.RED,
    "ORANGE": Color.ORANGE,
    "YELLOW": Color.YELLOW,
    "GREEN": Color.GREEN,
    "CYAN": Color.CYAN,
    "BLUE": Color.BLUE,
    "VIOLET": Color.VIOLET,
    "MAGENTA": Color.MAGENTA,
}
colors = ["RED", "ORANGE", "YELLOW", "GREEN", "CYAN", "BLUE", "VIOLET", "MAGENTA"]
color_index = 0
flag = True
wantedNumberOfBalls = 3
remainingNumberOfBallsCounter = 3
counter = 0

keyboard2 = poll()
keyboard2.register(stdin)

while True:
    inputFromTB = stdin.buffer.read(1)
    if inputFromTB == b"0":
        stdout.write("wfawefawefaw" + "\n")
        wait(20)
    elif inputFromTB == b"1":
        ballLifterExecution(
            wantedNumberOfBalls,
            remainingNumberOfBallsCounter,
            counter,
            flag,
            colors,
            color_index,
        )
        stdout.write("Done!" + "\n")
