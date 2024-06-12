# import numpy as np
# import matplotlib.pyplot as plt
# import math


# # Define the altered functions
# def calculate_energy_reward(motor_speed, max_energy=1510):
#     if motor_speed < 200:  # If motor speed is below 200 return static reward
#         return 1.93
#     energyFactor = 1.5
#     energy_expenditure = motor_speed * energyFactor
#     normalized_energy = energy_expenditure / max_energy
#     inverted_energy = 1 - normalized_energy
#     reward = math.exp(inverted_energy * 3) - math.exp(normalized_energy * 3)
#     return reward / 10 + 1


# # Define the altered time reward function
# def calculate_time_reward(execution_time, max_time=3000, threshold_time=2200):
#     if execution_time > threshold_time:
#         normalized_time = (execution_time - threshold_time) / (
#             max_time - threshold_time
#         )
#         reward = -2.2 * (normalized_time**0.6)
#     else:
#         normalized_time = execution_time / threshold_time
#         inverted_time = 1 - normalized_time
#         reward = 2.2 * (inverted_time**0.6)
#     return reward


# # Generate data for plotting
# motor_speeds = np.linspace(0, 1510, 300)
# execution_times = np.linspace(0, 3000, 300)

# energy_rewards = [calculate_energy_reward(speed) for speed in motor_speeds]
# time_rewards = [calculate_time_reward(time) for time in execution_times]

# # Plot the altered functions
# plt.figure(figsize=(14, 6))

# plt.subplot(1, 2, 1)
# plt.plot(motor_speeds, energy_rewards, label="Energy Reward")
# plt.xlabel("Motor Speed")
# plt.ylabel("Reward")
# plt.title("Energy Reward vs. Motor Speed (Negative for High Speed)")
# plt.legend()
# plt.grid(True)  # Show grid

# plt.subplot(1, 2, 2)
# plt.plot(execution_times, time_rewards, label="Time Reward", color="orange")
# plt.xlabel("Execution Time")
# plt.ylabel("Reward")
# plt.title("Time Reward vs. Execution Time (Smooth Transition)")
# plt.legend()
# plt.grid(True)  # Show grid

# plt.tight_layout()
# plt.show()

import numpy as np
import matplotlib.pyplot as plt


# Define the scaling and normalization functions
def scale_reward(normalized_reward):
    overall_reward = 2 * (1 / (1 + np.exp(-0.93 * normalized_reward))) - 1
    return overall_reward


def normalize_reward(combined_reward, threshold):
    normalized_reward = (
        combined_reward - threshold
    )  # Subtract threshold to center around 0
    return normalized_reward


def calculate_overall_reward(combined_reward, threshold):
    normalized_reward = normalize_reward(combined_reward, threshold)
    overall_reward = scale_reward(normalized_reward)
    return overall_reward


# Generate data for plotting
combined_rewards = np.linspace(-10, 10, 300)
threshold = 0

normalized_rewards = [normalize_reward(cr, threshold) for cr in combined_rewards]
overall_rewards = [scale_reward(nr) for nr in normalized_rewards]

# Plot the functions
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(combined_rewards, normalized_rewards, label="Normalized Reward")
plt.xlabel("Combined Reward")
plt.ylabel("Normalized Reward")
plt.title("Normalization of Combined Reward")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(combined_rewards, overall_rewards, label="Overall Reward", color="orange")
plt.xlabel("Combined Reward")
plt.ylabel("Overall Reward")
plt.title("Scaling of Normalized Reward to Overall Reward")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
