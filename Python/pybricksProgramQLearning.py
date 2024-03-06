from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from usys import stdin, stdout
from uselect import poll, select
from urandom import uniform, choice
from umath import exp

hub = PrimeHub()

colorSensor = ColorSensor(Port.A)
largeMotor = Motor(Port.C)
ballLifterMotor = Motor(Port.D)
ballStopperMotor = Motor(Port.F)

stopwatch = StopWatch()

epsilon = 0.9
alpha = 0.1
gamma = 0.9

# States, Actions, and Rewards
States = [Color.WHITE, Color.BLUE, Color.GREEN]

# Initialize Q-table with all Q-values equal to 0
qtable = {state: {action: 0 for action in range(50, 1010, 10)} for state in States}


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
        stdout.buffer.write("Energy Expenditure: " + str(50) + "\n")
        wait(20)
        stdout.buffer.write("Motor Speed: " + str(0) + "\n")
        wait(20)
        if colorSensor.color() == Color.WHITE:
            return Color.WHITE

        if current_color in desired_colors:
            wait(20)
            return current_color
        wait(20)


def setLargeMotor(numOfBalls):
    setMotorAngleShortestPath(largeMotor, 0, 300)
    largeMotor.reset_angle(0)
    wait(1000)
    largeMotor.run_target(1000, numOfBalls * 30, Stop.HOLD, wait=True)


def moveLargeMotorForInterval(remainingBalls):
    setMotorAngleShortestPath(largeMotor, remainingBalls * 30, 100)


# Function to choose action using epsilon-greedy policy
def choose_action(state, epsilon_in=epsilon):
    if epsilon_in > uniform(0, 1):
        available_speeds = [speed for speed in range(50, 1010, 10)]
        return choice(available_speeds)
    else:
        return max(qtable[state], key=qtable[state].get)


# Function to update Q-value based on Bellman equation
def update_q(state, action, reward, next_state):
    qvalue = qtable[state][action]
    new_q = (1 - alpha) * qvalue + alpha * (
        reward + gamma * max(qtable[next_state].values())
    )
    qtable[state][action] = new_q  # update Q-Table with new Q-Value
    # print("Updated Q-value for " + str(action) + ": " + str(qtable[state][action]))


def calculate_energy_reward(motor_speed, max_energy=1510):
    if motor_speed < 150:  # If motor speed is below 150 return static reward
        return 2
    # Increase in energy consumption with speed
    energyFactor = 1.5

    # Simulate energy expenditure based on speed
    energy_expenditure = motor_speed * energyFactor
    stdout.buffer.write("Energy Expenditure: " + str(energy_expenditure) + "\n")
    normalized_energy = energy_expenditure / max_energy
    inverted_energy = 1 - normalized_energy
    reward = exp(inverted_energy * 3.5)
    return reward / 10


def calculate_time_reward(execution_time, max_time=3000):
    normalized_time = execution_time / max_time
    inverted_time = 1 - normalized_time
    reward = exp(inverted_time * 6)
    return reward / 10


def ballLifterExecution(
    numOfBallsWanted, numOfBallsRemaining, counter, firstIterationFlag, epsilon
):

    keyboard1 = poll()
    keyboard1.register(stdin)

    ballLifterMotorStopWatch = StopWatch()

    blueCounter = 0
    greenCounter = 0
    whiteCounter = 0

    colors = [Color.WHITE, Color.BLUE, Color.GREEN]

    stdout.buffer.write("Blue Counter: " + str(blueCounter) + "\n")
    wait(20)
    stdout.buffer.write("Green Counter: " + str(greenCounter) + "\n")
    wait(20)
    stdout.buffer.write("White Counter: " + str(whiteCounter) + "\n")
    wait(20)

    while not keyboard1.poll(0):
        if firstIterationFlag:
            setLargeMotor(numOfBallsWanted)
            hub.display.number(counter)
            firstIterationFlag = False

        detected_color = waitForColor(colors)
        setMotorAngleShortestPath(ballStopperMotor, 0, 300)

        chosen_action = choose_action(detected_color, epsilon_in=epsilon)

        moveLargeMotorForInterval(numOfBallsRemaining)

        stdout.buffer.write("Ball Color: " + str(detected_color) + "\n")
        hub.light.on(detected_color)
        wait(1000)
        if not keyboard1.poll(0):
            start_lift_time = ballLifterMotorStopWatch.time()
            stdout.buffer.write("Motor Speed: " + str(chosen_action) + "\n")

            # Lifts the arm
            setMotorAngleShortestPath(ballLifterMotor, 310, chosen_action)
            setMotorAngleLongestPath(ballLifterMotor, 35, chosen_action, True)
            setMotorAngleLongestPath(ballLifterMotor, 320, chosen_action, False)

            start_time = stopwatch.time()  # Track time for success/fail

            setMotorAngleShortestPath(ballStopperMotor, 310, 200)

            success = False

            total_lift_time = 5000
            while stopwatch.time() - start_time < 3000:  # 3-second timeout
                if colorSensor.color() == detected_color:
                    total_lift_time = ballLifterMotorStopWatch.time() - start_lift_time
                    success = True
                    counter += 1
                    numOfBallsRemaining -= 1
                    moveLargeMotorForInterval(numOfBallsRemaining)
                    hub.display.number(counter)
                    break
                wait(20)
            if counter == numOfBallsWanted:
                break

            stdout.buffer.write("Balls Counter: " + str(counter) + "\n")

            if detected_color == Color.BLUE:
                blueCounter += 1
                stdout.buffer.write("Blue Counter: " + str(blueCounter) + "\n")
            elif detected_color == Color.GREEN:
                greenCounter += 1
                stdout.buffer.write("Green Counter: " + str(greenCounter) + "\n")
            elif detected_color == Color.WHITE:
                whiteCounter += 1
                stdout.buffer.write("White Counter: " + str(whiteCounter) + "\n")

            energy_reward = calculate_energy_reward(chosen_action)
            # print("Energy Reward: " + str(energy_reward))
            time_reward = calculate_time_reward(total_lift_time)
            # print("Total Lift Time: " + str(total_lift_time))
            # print("Time Reward: " + str(time_reward))
            success_reward = 1 if success else -1  # Adjust as needed
            combined_reward = success_reward * (energy_reward + (2 * time_reward))
            # print("Combined Reward: " + str(combined_reward))

            update_q(detected_color, chosen_action, combined_reward, detected_color)

            # Decrease epsilon for more exploitation in later training phases
            if epsilon > 0.4:
                epsilon -= 0.01

    setMotorAngleShortestPath(ballStopperMotor, 310, 200)


while True:
    keyboard2 = poll()
    keyboard2.register(stdin)
    pressed = []
    counter = 0
    flag = True
    stdout.buffer.write("Motor Speed: " + str(0) + "\n")

    while not any(pressed):
        pressed = hub.buttons.pressed()
        hub.display.icon(Icon.HEART)
        hub.light.on(Color.ORANGE)
        stdout.buffer.write("Energy Expenditure: " + str(50) + "\n")
        wait(100)
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
            stdout.buffer.write("Energy Expenditure: " + str(50) + "\n")
            wait(100)
        inputFromTB = stdin.buffer.read(2)

        if (
            int.from_bytes(inputFromTB, "big") >= 0
            and int.from_bytes(inputFromTB, "big") <= 50
        ):
            numberOfBalls = int.from_bytes(inputFromTB, "big")
            ballLifterExecution(numberOfBalls, numberOfBalls, counter, flag, epsilon)
            stdout.buffer.write("Done!" + "\n")
