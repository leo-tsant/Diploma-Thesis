import matplotlib.pyplot as plt

# Data for the balls at a motor speed of 500
weight_500 = [1.7, 4.4, 5.4, 6.8]
average_reward_500 = [2.647567, 3.083964, 3.039486, 3.030054]

# Ideal motor speeds and corresponding average rewards
ideal_speeds = [700, 750, 650, 650]
ideal_rewards = [2.805882, 3.305734, 3.239922, 3.321411]

# # Create the first graph for motor speed 500
# plt.figure(figsize=(10, 6))
# plt.scatter(weight_500, average_reward_500, label="Motor Speed 500")
# plt.xlabel("Weight (g)")
# plt.ylabel("Average Reward")
# plt.title("Average Reward vs Weight (Motor Speed 500)")
# plt.grid(True)
# plt.show()

# Create the second graph with motor speed 500 and ideal results
plt.figure(figsize=(10, 6))
plt.scatter(weight_500, average_reward_500, label="Motor Speed 500")
plt.scatter(weight_500, ideal_rewards, label="Ideal Speed")

# Add markers for ideal speeds and rewards
for i, (weight, speed, reward) in enumerate(
    zip(weight_500, ideal_speeds, ideal_rewards)
):
    plt.scatter(weight, reward, marker="o", color="orange", zorder=3)
    plt.annotate(
        f" Speed: {speed}, \n Avg Reward: {reward:.4f}",
        (weight, reward),
        xytext=(5, -5),
        textcoords="offset points",
        fontsize=8,
        ha="left",
    )

plt.xlabel("Weight (g)")
plt.ylabel("Average Reward")
plt.title("Average Reward vs Weight (Motor Speed 500 and Ideal)")
plt.legend()
plt.grid(True)
plt.show()
