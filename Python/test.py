# import matplotlib.pyplot as plt
# import numpy as np


# def calculate_energy_reward(motor_speed, max_energy=1510):
#     # Increase in energy consumption with speed
#     energyFactor = 1.5

#     # Simulate energy expenditure based on speed
#     energy_expenditure = motor_speed * energyFactor

#     normalized_energy = energy_expenditure / max_energy
#     inverted_energy = 1 - normalized_energy
#     reward = np.exp(inverted_energy * 3)  # Adjust '4' to control steepness
#     return reward / 10


# def calculate_time_reward(execution_time, max_time=3000):
#     normalized_time = execution_time / max_time
#     inverted_time = 1 - normalized_time
#     reward = np.exp(inverted_time * 6)  # Adjust '4' to control steepness
#     return reward / 10


# # Sample input ranges (same as before)
# motor_speed_values = np.arange(50, 1000, 10)
# time_values = np.arange(1000, 3000, 20)

# # Calculate rewards
# energy_rewards = calculate_energy_reward(motor_speed_values)
# time_rewards = calculate_time_reward(time_values)

# # Plot the results
# plt.figure(figsize=(10, 5))

# plt.subplot(1, 2, 1)
# plt.plot(motor_speed_values, energy_rewards)
# plt.xlabel("Motor Speed (deg/s)")
# plt.ylabel("Reward")
# plt.title("Energy Reward Function")

# plt.subplot(1, 2, 2)
# plt.plot(time_values, time_rewards)
# plt.xlabel("Execution Time (ms)")
# plt.ylabel("Reward")
# plt.title("Time Reward Function")

# plt.tight_layout()
# plt.show()

# Original string representation of the Q-Table
q_table_str = "Q-Table: {0.0: {300: -0.09135488, 600: 0.03944802, 900: 0, 50: 0, 350: -0.09011816, 650: 0, 950: 0, 100: -0.0941273, 400: -0.08707205, 700: 0.08263496, 1000: 0, 150: -0.099923, 450: -0.08282918, 750: 0, 200: 0, 500: 0, 800: -0.009913654, 250: 0, 550: 0, 850: 0.03000485}}"

# Convert the string to a dictionary
q_table_dict = eval(q_table_str.replace("Q-Table: ", ""))

# Initialize an empty dictionary to hold the sorted Q-Table
sorted_q_table = {}

# Iterate over each label in the Q-Table
for label, sub_dict in q_table_dict.items():
    # Sort the sub-dictionary based on the values in descending order
    sorted_items = sorted(sub_dict.items(), key=lambda x: x[1], reverse=True)
    # Convert the sorted items back into a dictionary and add it to the sorted Q-Table
    sorted_q_table[label] = {k: v for k, v in sorted_items}

# Print the sorted Q-Table
print(sorted_q_table)
