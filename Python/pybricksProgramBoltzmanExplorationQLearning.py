from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from usys import stdin, stdout
from uselect import poll, select
from urandom import uniform, choice
from umath import exp
from ustruct import unpack

hub = PrimeHub()

colorSensor = ColorSensor(Port.A)
largeMotor = Motor(Port.C)
ballLifterMotor = Motor(Port.D)
ballStopperMotor = Motor(Port.F)

stopwatch = StopWatch()

epsilon = 0.9
alpha = 0.1
gamma = 0.9

states = []
chosen_speeds = []  # List to store the chosen speeds and their iterations
qtable = {}

global total_energy_exp
global total_execution_time
global avg_reward


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
def waitForColor():
    while True:
        if colorSensor.color() != Color.NONE:
            break
        stdout.buffer.write("Energy Expenditure: " + str(50) + "\n")
        wait(20)


def setLargeMotor(numOfBalls):
    setMotorAngleShortestPath(largeMotor, 0, 1000)
    largeMotor.reset_angle(0)
    wait(1000)
    largeMotor.run_target(1000, numOfBalls * 30, Stop.HOLD, wait=True)


def moveLargeMotorForInterval(remainingBalls):
    setMotorAngleShortestPath(largeMotor, remainingBalls * 30, 100)


# Handle weight fluctuations and avoid creating unnecessary states
def find_closest_state(weight):
    weight_tolerance = 0.1
    for existing_state in qtable:
        if abs(existing_state - weight) <= weight_tolerance:
            return existing_state
    return None  # If no state is within tolerance


# Function to choose action using epsilon-greedy policy
def choose_action(state, epsilon_in=epsilon, temperature=1.0):
    if epsilon_in > uniform(0, 1):
        available_speeds = [
            speed for speed in range(50, 1050, 50) if qtable[state].get(speed, -1) >= 0
        ]
        stdout.buffer.write("Available Speeds: " + str(available_speeds) + "\n")

        # Calculate Boltzmann weights
        q_values = [qtable[state][speed] for speed in available_speeds]
        exp_values = [exp(q / temperature) for q in q_values]
        total_weight = sum(exp_values)

        # Generate a random number within the total weight
        rand_num = uniform(0, total_weight)

        # Select the speed based on the random number and weights
        weight_sum = 0
        for i, speed in enumerate(available_speeds):
            weight_sum += exp_values[i]
            if rand_num <= weight_sum:
                return speed
    else:
        return max(qtable[state], key=qtable[state].get)


def update_q(state, action, reward, next_state):
    qvalue = qtable[state][action]
    new_q = (1 - alpha) * qvalue + alpha * (
        reward + gamma * max(qtable[next_state].values())
    )
    qtable[state][action] = new_q  # update Q-Table with new Q-Value
    # stdout.buffer.write("Updated Q-value for state " + str(state) + " and action " + str(action) + ": " + str(qtable[state][action]) + '\n')


def calculate_energy_reward(motor_speed, max_energy=1510):
    if motor_speed < 200:  # If motor speed is below 200 return static reward
        return 1.93
    energyFactor = 1.5
    energy_expenditure = motor_speed * energyFactor
    stdout.buffer.write("Energy Expenditure: " + str(energy_expenditure) + "\n")
    normalized_energy = energy_expenditure / max_energy
    inverted_energy = 1 - normalized_energy
    reward = exp(inverted_energy * 3) - exp(normalized_energy * 3)
    return reward / 10 + 1


# Define the altered time reward function
def calculate_time_reward(execution_time, max_time=3000, threshold_time=2200):
    if execution_time > threshold_time:
        normalized_time = (execution_time - threshold_time) / (
            max_time - threshold_time
        )
        reward = -2.2 * (normalized_time**0.6)
    else:
        normalized_time = execution_time / threshold_time
        inverted_time = 1 - normalized_time
        reward = 2.2 * (inverted_time**0.6)
    return reward


def scale_reward(normalized_reward):
    overall_reward = 2 * (1 / (1 + exp(-5 * normalized_reward))) - 1
    return overall_reward


def normalize_reward(combined_reward):
    normalized_reward = combined_reward / 1
    return normalized_reward


def calculate_overall_reward(combined_reward):
    normalized_reward = normalize_reward(combined_reward)
    overall_reward = scale_reward(normalized_reward)
    return overall_reward


def ballLifterExecution(
    numOfBallsWanted, numOfBallsRemaining, counter, firstIterationFlag, epsilon, weight
):
    global total_energy_exp  # Access the global variable
    global total_execution_time
    global avg_reward
    global chosen_speeds

    ballLifterMotorStopWatch = StopWatch()

    keyboard1 = poll()
    keyboard1.register(stdin)

    total_reward = 0
    total_energy_exp = 0  # Initialize inside the function
    iteration = 0  # Track the iteration number
    combined_rewards_array = []

    while not keyboard1.poll(0):
        if firstIterationFlag:
            # setLargeMotor(numOfBallsWanted)
            setMotorAngleShortestPath(ballStopperMotor, 0, 300)
            hub.display.number(counter)
            firstIterationFlag = False
            success = True
            waitForColor()
            start_total_time = ballLifterMotorStopWatch.time()

        if success == False:
            waitForColor()

        chosen_action = choose_action(weight, epsilon_in=epsilon)
        wait(20)

        # Store the chosen action and iteration
        chosen_speeds.append((iteration, chosen_action))
        iteration += 1

        # moveLargeMotorForInterval(numOfBallsRemaining)

        wait(100)
        if not keyboard1.poll(0):
            start_lift_time = ballLifterMotorStopWatch.time()
            stdout.buffer.write("Motor Speed: " + str(chosen_action) + "\n")

            # Lifts the arm
            setMotorAngleShortestPath(ballLifterMotor, 340, chosen_action)
            setMotorAngleLongestPath(ballLifterMotor, 40, chosen_action, True)
            wait(400)
            setMotorAngleLongestPath(ballLifterMotor, 350, 800, False)

            start_time = stopwatch.time()  # Track time for success/fail

            success = False

            total_lift_time = 5000
            while stopwatch.time() - start_time < 3000:  # 3-second timeout
                if colorSensor.color() != Color.NONE:
                    total_lift_time = ballLifterMotorStopWatch.time() - start_lift_time
                    success = True
                    counter += 1
                    numOfBallsRemaining -= 1
                    # moveLargeMotorForInterval(numOfBallsRemaining)
                    hub.display.number(counter)
                    break
                wait(20)

            energy_expenditure = chosen_action * 1.5
            total_energy_exp += energy_expenditure
            energy_reward = calculate_energy_reward(chosen_action)
            wait(20)
            # stdout.buffer.write("Energy Reward: " + str(energy_reward) + '\n')
            time_reward = calculate_time_reward(total_lift_time)
            # wait(20)
            # stdout.buffer.write("Total Lift Time: " + str(total_lift_time) + '\n')
            # wait(20)
            # stdout.buffer.write("Time Reward: " + str(time_reward) + '\n')
            # wait(20)
            success_reward = 1 if success else -10
            combined_reward = success_reward * (2 * energy_reward + (3 * time_reward))
            if success_reward < 0 and combined_reward > 0:
                combined_reward = -combined_reward
            # wait(20)
            # stdout.buffer.write("Combined Reward: " + str(combined_reward) + '\n')
            # wait(20)

            update_q(weight, chosen_action, combined_reward, weight)
            wait(20)

            epsilon_decay_rate = 0.995  # Reduce epsilon slightly each iteration
            epsilon *= epsilon_decay_rate
            # wait(20)
            # stdout.buffer.write("Epsilon: " + str(epsilon) + '\n')
            # wait(20)
            stdout.buffer.write("Balls Counter: " + str(counter) + "\n")
            wait(10)
            stdout.buffer.write("\n")

            if counter == numOfBallsWanted:
                stdout.buffer.write("Done!" + "\n")
                total_execution_time = (
                    ballLifterMotorStopWatch.time() - start_total_time
                )
                avg_reward = total_reward / numOfBallsWanted
                break

    setMotorAngleShortestPath(ballStopperMotor, 310, 200)


while True:
    keyboard2 = poll()
    keyboard2.register(stdin)

    pressed = []
    counter = 0
    flag = True
    stdout.buffer.write("Motor Speed: " + str(0) + "\n")
    wait(10)
    stdout.buffer.write("Select Mode: " + "\n")

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
        stdout.buffer.write("Selected Mode: Training" + "\n")
    elif Button.RIGHT in pressed:
        mode = "Testing"
        epsilon = 0  # Set epsilon to 0 for testing
        hub.display.icon(Icon.ARROW_RIGHT)
        stdout.buffer.write("Selected Mode: Testing" + "\n")
    else:
        mode = "Waiting"

    if mode in ["Training", "Testing"]:
        stdout.buffer.write("Select Number of Balls" + "\n")
        wait(20)
        while not keyboard2.poll(0):
            stdout.buffer.write("Energy Expenditure: " + str(50) + "\n")
            wait(100)
        inputFromTB = stdin.buffer.read(2)

        if (
            int.from_bytes(inputFromTB, "big") >= 0
            and int.from_bytes(inputFromTB, "big") <= 99
        ):
            numberOfBalls = int.from_bytes(inputFromTB, "big")
            keyboard3 = poll()
            keyboard3.register(stdin)
            stdout.buffer.write("Waiting to get weight of the ball..." + "\n")
            while not keyboard3.poll(0):
                hub.light.on(Color.MAGENTA)
                wait(100)
            hub.light.on(Color.RED)
            inputFromArduino = stdin.buffer.read(4)
            weight = unpack("!f", inputFromArduino)[0]
            stdout.buffer.write("Weight received: " + str(weight) + "\n")

            closest_state = find_closest_state(weight)
            wait(20)
            stdout.buffer.write("Closest state " + str(closest_state) + "\n")
            if closest_state:
                # State within tolerance exists
                weight = closest_state
            else:
                # Create a new state
                states.append(weight)
                qtable[weight] = {action: 0 for action in range(50, 1050, 50)}
            ballLifterExecution(
                numberOfBalls, numberOfBalls, counter, flag, epsilon, weight
            )
            # stdout.buffer.write("Q-Table: " + str(qtable) + '\n')
            stdout.buffer.write("Chosen Speeds: " + str(chosen_speeds) + "\n")
            # stdout.buffer.write("Total Time: " + str(total_execution_time) + '\n')
            # wait(20)
            # stdout.buffer.write('Total Energy Expenditure: ' + str(total_energy_exp) + '\n')
            # wait(20)
            # stdout.buffer.write('Avg Reward: ' + str(avg_reward) + '\n')
            for state, inner_dict in qtable.items():
                # Create a temporary list to store top 3 elements (key, value pairs)
                top_three = []
                # Iterate through each key-value pair in the inner dictionary
                for key, value in inner_dict.items():
                    # Check if the current element is one of the top 3 (considering both key and value)
                    if len(top_three) < 3 or value > top_three[-1][1]:
                        # If it's one of the top 3, either add it directly or replace the lowest value
                        if len(top_three) < 3:
                            top_three.append((key, value))
                        else:
                            top_three[-1] = (key, value)
                        # Since we only care about the top 3, keep the list sorted by value (descending)
                        top_three.sort(key=lambda x: x[1], reverse=True)
                # Print the state and the top 3 elements
                print(f"State {state}:")
                for i, (key, value) in enumerate(top_three, 1):
                    print(f"{i}. Speed: {key}, Q-Value: {value}")
                    wait(20)
