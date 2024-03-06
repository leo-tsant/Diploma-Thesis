import matplotlib.pyplot as plt
import numpy as np


def calculate_energy_reward(motor_speed, max_energy=1510):
    # Increase in energy consumption with speed
    energyFactor = 1.5

    # Simulate energy expenditure based on speed
    energy_expenditure = motor_speed * energyFactor

    normalized_energy = energy_expenditure / max_energy
    inverted_energy = 1 - normalized_energy
    reward = np.exp(inverted_energy * 3.5)  # Adjust '4' to control steepness
    return reward / 10


def calculate_time_reward(execution_time, max_time=3000):
    normalized_time = execution_time / max_time
    inverted_time = 1 - normalized_time
    reward = np.exp(inverted_time * 6)  # Adjust '4' to control steepness
    return reward / 10


# Sample input ranges (same as before)
motor_speed_values = np.arange(50, 1000, 10)
time_values = np.arange(1000, 3000, 20)

# Calculate rewards
energy_rewards = calculate_energy_reward(motor_speed_values)
time_rewards = calculate_time_reward(time_values)

# Plot the results
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(motor_speed_values, energy_rewards)
plt.xlabel("Motor Speed (deg/s)")
plt.ylabel("Reward")
plt.title("Energy Reward Function")

plt.subplot(1, 2, 2)
plt.plot(time_values, time_rewards)
plt.xlabel("Execution Time (ms)")
plt.ylabel("Reward")
plt.title("Time Reward Function")

plt.tight_layout()
plt.show()
