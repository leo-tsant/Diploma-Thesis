# import matplotlib.pyplot as plt

# # Data for the balls at a motor speed of 500
# weight_500 = [1.7, 4.4, 5.4, 6.8]
# average_reward_500 = [2.647567, 3.083964, 3.039486, 3.030054]

# # Ideal motor speeds and corresponding average rewards
# ideal_speeds = [700, 750, 650, 650]
# ideal_rewards = [2.805882, 3.305734, 3.239922, 3.321411]

# # # Create the first graph for motor speed 500
# # plt.figure(figsize=(10, 6))
# # plt.scatter(weight_500, average_reward_500, label="Motor Speed 500")
# # plt.xlabel("Weight (g)")
# # plt.ylabel("Average Reward")
# # plt.title("Average Reward vs Weight (Motor Speed 500)")
# # plt.grid(True)
# # plt.show()

# # Create the second graph with motor speed 500 and ideal results
# plt.figure(figsize=(10, 6))
# plt.scatter(weight_500, average_reward_500, label="Motor Speed 500")
# plt.scatter(weight_500, ideal_rewards, label="Ideal Speed")

# # Add markers for ideal speeds and rewards
# for i, (weight, speed, reward) in enumerate(
#     zip(weight_500, ideal_speeds, ideal_rewards)
# ):
#     plt.scatter(weight, reward, marker="o", color="orange", zorder=3)
#     plt.annotate(
#         f" Speed: {speed}, \n Avg Reward: {reward:.4f}",
#         (weight, reward),
#         xytext=(5, -5),
#         textcoords="offset points",
#         fontsize=8,
#         ha="left",
#     )

# plt.xlabel("Weight (g)")
# plt.ylabel("Average Reward")
# plt.title("Average Reward vs Weight (Motor Speed 500 and Ideal)")
# plt.legend()
# plt.grid(True)
# plt.show()

import matplotlib.pyplot as plt

set_1 = [
    (0, 200),
    (1, 950),
    (2, 350),
    (3, 850),
    (4, 100),
    (5, 50),
    (6, 550),
    (7, 800),
    (8, 550),
    (9, 600),
    (10, 300),
    (11, 150),
    (12, 500),
    (13, 600),
    (14, 750),
    (15, 450),
    (16, 600),
    (17, 800),
    (18, 700),
    (19, 600),
    (20, 450),
    (21, 650),
    (22, 650),
    (23, 550),
    (24, 400),
    (25, 550),
    (26, 250),
    (27, 550),
    (28, 550),
    (29, 550),
    (30, 550),
    (31, 550),
    (32, 550),
    (33, 550),
    (34, 550),
    (35, 550),
    (36, 550),
    (37, 550),
    (38, 550),
    (39, 550),
    (40, 550),
    (41, 550),
]

set_2 = [
    (0, 350),
    (1, 600),
    (2, 100),
    (3, 950),
    (4, 550),
    (5, 650),
    (6, 400),
    (7, 300),
    (8, 1000),
    (9, 800),
    (10, 150),
    (11, 650),
    (12, 700),
    (13, 50),
    (14, 900),
    (15, 550),
    (16, 550),
    (17, 700),
    (18, 200),
    (19, 250),
    (20, 650),
    (21, 550),
    (22, 850),
    (23, 550),
    (24, 550),
    (25, 550),
    (26, 600),
    (27, 550),
    (28, 550),
    (29, 550),
    (30, 550),
    (31, 550),
    (32, 550),
    (33, 550),
    (34, 550),
    (35, 550),
    (36, 550),
    (37, 550),
    (38, 550),
    (39, 550),
]

set_3 = [
    (0, 750),
    (1, 800),
    (2, 600),
    (3, 50),
    (4, 1000),
    (5, 900),
    (6, 950),
    (7, 450),
    (8, 600),
    (9, 750),
    (10, 200),
    (11, 150),
    (12, 550),
    (13, 250),
    (14, 600),
    (15, 850),
    (16, 600),
    (17, 600),
    (18, 650),
    (19, 600),
    (20, 300),
    (21, 600),
    (22, 600),
    (23, 600),
    (24, 400),
    (25, 600),
    (26, 600),
    (27, 600),
    (28, 600),
    (29, 600),
    (30, 600),
    (31, 600),
    (32, 600),
    (33, 600),
    (34, 600),
    (35, 600),
    (36, 600),
    (37, 600),
    (38, 600),
]

set_4 = [
    (0, 550),
    (1, 300),
    (2, 200),
    (3, 650),
    (4, 550),
    (5, 50),
    (6, 900),
    (7, 750),
    (8, 600),
    (9, 600),
    (10, 150),
    (11, 650),
    (12, 600),
    (13, 650),
    (14, 1000),
    (15, 250),
    (16, 100),
    (17, 650),
    (18, 600),
    (19, 650),
    (20, 600),
    (21, 950),
    (22, 550),
    (23, 450),
    (24, 400),
    (25, 400),
    (26, 700),
    (27, 550),
    (28, 550),
    (29, 550),
    (30, 550),
    (31, 550),
    (32, 550),
    (33, 550),
    (34, 550),
    (35, 550),
    (36, 550),
    (37, 550),
    (38, 550),
    (39, 550),
]

set_5 = [
    (0, 750),
    (1, 450),
    (2, 900),
    (3, 700),
    (4, 700),
    (5, 700),
    (6, 300),
    (7, 450),
    (8, 800),
    (9, 600),
    (10, 750),
    (11, 850),
    (12, 500),
    (13, 200),
    (14, 550),
    (15, 350),
    (16, 700),
    (17, 600),
    (18, 750),
    (19, 150),
    (20, 500),
    (21, 600),
    (22, 100),
    (23, 250),
    (24, 650),
    (25, 450),
    (26, 400),
    (27, 1000),
    (28, 600),
    (29, 600),
    (30, 50),
    (31, 450),
    (32, 600),
    (33, 450),
    (34, 450),
    (35, 600),
    (36, 600),
    (37, 450),
    (38, 450),
    (39, 450),
    (40, 450),
    (41, 450),
    (42, 450),
    (43, 450),
    (44, 450),
    (45, 450),
    (46, 450),
    (47, 450),
]

set_6 = [
    (0, 250),
    (1, 600),
    (2, 450),
    (3, 500),
    (4, 850),
    (5, 100),
    (6, 750),
    (7, 400),
    (8, 500),
    (9, 50),
    (10, 450),
    (11, 150),
    (12, 1000),
    (13, 550),
    (14, 950),
    (15, 500),
    (16, 500),
    (17, 500),
    (18, 800),
    (19, 450),
    (20, 350),
    (21, 450),
    (22, 400),
    (23, 500),
    (24, 450),
    (25, 500),
    (26, 500),
    (27, 500),
    (28, 500),
    (29, 500),
    (30, 500),
    (31, 500),
    (32, 500),
    (33, 500),
]


def plot_chosen_speeds(speeds_1, speeds_2, speeds_3, speeds_4, speeds_5, speeds_6):
    # Unpack iterations and chosen speeds for each set
    iterations_1, chosen_speeds_1 = zip(*speeds_1)
    iterations_2, chosen_speeds_2 = zip(*speeds_2)
    iterations_3, chosen_speeds_3 = zip(*speeds_3)
    iterations_4, chosen_speeds_4 = zip(*speeds_4)
    iterations_5, chosen_speeds_5 = zip(*speeds_5)
    iterations_6, chosen_speeds_6 = zip(*speeds_6)

    # Create a figure with 2 rows and 3 columns
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))  # Adjust figsize as needed

    # Plots for the six sets
    axs[0, 0].plot(iterations_1, chosen_speeds_1, marker="o")
    axs[0, 0].set_xlabel("Iteration")
    axs[0, 0].set_ylabel("Chosen Speed")
    axs[0, 0].set_title("(Set 1)")
    axs[0, 0].grid(True)

    axs[0, 1].plot(iterations_2, chosen_speeds_2, marker="o")
    axs[0, 1].set_xlabel("Iteration")
    # axs[0, 1].set_ylabel("Chosen Speed")  # Shared y-label for top row
    axs[0, 1].set_title("(Set 2)")
    axs[0, 1].grid(True)

    axs[0, 2].plot(iterations_3, chosen_speeds_3, marker="o")
    axs[0, 2].set_xlabel("Iteration")
    # axs[0, 2].set_ylabel("Chosen Speed")  # Shared y-label for top row
    axs[0, 2].set_title("(Set 3)")
    axs[0, 2].grid(True)

    axs[1, 0].plot(iterations_4, chosen_speeds_4, marker="o")
    axs[1, 0].set_xlabel("Iteration")
    axs[1, 0].set_ylabel("Chosen Speed")
    axs[1, 0].set_title("(Set 4)")
    axs[1, 0].grid(True)

    axs[1, 1].plot(iterations_5, chosen_speeds_5, marker="o")
    axs[1, 1].set_xlabel("Iteration")
    # axs[1, 1].set_ylabel("Chosen Speed")  # Shared y-label for bottom row
    axs[1, 1].set_title("(Set 5)")
    axs[1, 1].grid(True)

    axs[1, 2].plot(iterations_6, chosen_speeds_6, marker="o")
    axs[1, 2].set_xlabel("Iteration")
    # axs[1, 2].set_ylabel("Chosen Speed")  # Shared y-label for bottom row
    axs[1, 2].set_title("(Set 6)")
    axs[1, 2].grid(True)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Display the plots
    plt.show()


# Call the function with the provided data
plot_chosen_speeds(set_1, set_2, set_3, set_4, set_5, set_6)
