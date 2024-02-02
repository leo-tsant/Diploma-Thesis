from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from usys import stdin, stdout
from uselect import poll, select
from urandom import uniform, choice

hub = PrimeHub()

colorSensor = ColorSensor(Port.A)
largeMotor = Motor(Port.C)
ballLifterMotor = Motor(Port.D)
ballStopperMotor = Motor(Port.F)

num_episodes = 3
num_iterations_per_episode = 15
epsilon = 0.9
alpha = 0.1
gamma = 0.9

# States, Actions, and Rewards
States = [Color.WHITE, Color.BLUE, Color.GREEN]
Actions = [250, 350, 800]
Rewards = {Color.WHITE: [1, -1, -1], Color.BLUE: [-1, 1, -1], Color.GREEN: [-1, -1, 1]}

# Initialize Q-table with all Q-values equal to 0
qtable = {state: {action: 0 for action in Actions} for state in States}


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


def setMotorAngleLongestPath(motor, target_angle, speed, waitFlag):
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
    motor.run_target(speed, target_angle, Stop.HOLD, wait=waitFlag)


# This is a function that waits for a desired color.
def waitForColor(desired_colors):
    # While the color is not in the desired colors, we keep waiting.
    while True:
        current_color = colorSensor.color()

        if current_color in desired_colors:
            wait(20)
            return current_color
        wait(20)


def setLargeMotor(numOfBalls):
    setMotorAngleShortestPath(largeMotor, 0, 300)
    largeMotor.reset_angle(0)
    wait(1000)
    largeMotor.run_target(200, numOfBalls * 30, Stop.HOLD, wait=True)


def moveLargeMotorForInterval(remainingBalls):
    setMotorAngleShortestPath(largeMotor, remainingBalls * 30, 100)


# Function to choose action using epsilon-greedy policy
def choose_action(state, epsilon_in=epsilon):
    if epsilon_in > uniform(0, 1):
        # Exploration: pick a random action from the action space
        return choice(Actions)
    else:
        # Exploitation: pick the action with the maximum Q-value
        return max(qtable[state], key=qtable[state].get)


# Function to update Q-value based on Bellman equation
def update_q(state, action, reward, next_state):
    qvalue = qtable[state][action]
    new_q = (1 - alpha) * qvalue + alpha * (
        reward + gamma * max(qtable[next_state].values())
    )
    qtable[state][action] = new_q  # update Q-Table with new Q-Value


def ballLifterExecution(
    numOfBallsWanted, numOfBallsRemaining, counter, firstIterationFlag, epsilon
):
    # setMotorAngleShortestPath(ballLifterMotor, 140, 300) # These adjustments are made so the ballLifterMotor resets it's position
    # ballLifterMotor.reset_angle(-219)                    # every time the program is executed regardless of its starting position

    keyboard1 = poll()
    keyboard1.register(stdin)

    blueCounter = 0
    greenCounter = 0
    whiteCounter = 0

    stdout.buffer.write("Blue Counter: " + str(blueCounter) + "\n")
    wait(20)
    stdout.buffer.write("Green Counter: " + str(greenCounter) + "\n")
    wait(20)
    stdout.buffer.write("White Counter: " + str(whiteCounter) + "\n")
    wait(20)

    setMotorAngleShortestPath(ballStopperMotor, 0, 300)

    while not keyboard1.poll(0):
        if firstIterationFlag:
            setLargeMotor(numOfBallsWanted)
            hub.display.number(counter)
            firstIterationFlag = False
        detected_color = waitForColor([Color.WHITE, Color.BLUE, Color.GREEN])

        moveLargeMotorForInterval(numOfBallsRemaining)

        stdout.buffer.write("Ball Color: " + str(detected_color) + "\n")
        hub.light.on(detected_color)
        wait(1000)
        if not keyboard1.poll(0):
            if counter == numOfBallsWanted:
                break

            chosen_action = choose_action(detected_color, epsilon_in=epsilon)

            # Lifts the arm
            setMotorAngleShortestPath(ballLifterMotor, 310, chosen_action)
            setMotorAngleLongestPath(ballLifterMotor, 35, chosen_action, True)
            setMotorAngleLongestPath(ballLifterMotor, 320, chosen_action, False)

            counter += 1
            hub.display.number(counter)
            stdout.buffer.write("Balls Counter: " + str(counter) + "\n")

            wait(20)

            if detected_color == Color.BLUE:
                blueCounter += 1
                stdout.buffer.write("Blue Counter: " + str(blueCounter) + "\n")
            elif detected_color == Color.GREEN:
                greenCounter += 1
                stdout.buffer.write("Green Counter: " + str(greenCounter) + "\n")
            elif detected_color == Color.WHITE:
                whiteCounter += 1
                stdout.buffer.write("White Counter: " + str(whiteCounter) + "\n")

            reward = Rewards[detected_color]
            update_q(
                detected_color,
                chosen_action,
                reward[Actions.index(chosen_action)],
                detected_color,
            )

            numOfBallsRemaining -= 1

            # Decrease epsilon for more exploitation in later training phases
            if epsilon > 0.4:
                epsilon -= 0.1

    setMotorAngleShortestPath(ballStopperMotor, 310, 200)


while True:
    keyboard2 = poll()
    keyboard2.register(stdin)
    pressed = []
    counter = 0
    flag = True

    while not any(pressed):
        pressed = hub.buttons.pressed()
        hub.display.icon(Icon.HEART)
        wait(10)
    # Wait for all buttons to be released.
    while any(hub.buttons.pressed()):
        wait(10)
    if Button.LEFT in pressed:
        mode = "Training"
        epsilon = 0.9  # Reset epsilon for each training episode
        hub.display.icon(Icon.ARROW_LEFT)
    elif Button.RIGHT in pressed:
        mode = "Testing"
        epsilon = 0  # Set epsilon to 0 for testing
        hub.display.icon(Icon.ARROW_RIGHT)
    else:
        mode = "Waiting"

    if mode in ["Training", "Testing"]:
        while not keyboard2.poll(0):
            wait(10)
        inputFromTB = stdin.buffer.read(2)

        if (
            int.from_bytes(inputFromTB, "big") >= 0
            and int.from_bytes(inputFromTB, "big") <= 50
        ):
            numberOfBalls = int.from_bytes(inputFromTB, "big")
            ballLifterExecution(numberOfBalls, numberOfBalls, counter, flag, epsilon)
            stdout.buffer.write("Done!" + "\n")
