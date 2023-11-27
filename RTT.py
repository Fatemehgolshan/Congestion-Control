import matplotlib.pyplot as plt
import numpy as np

# Create an empty list to store the RTT values
rtt = []

# Read the RTT values from the file
with open("tcp_reno_simulation_50percent.rtt", "r") as f:
    for line in f:
        rtt.append(float(line.strip()))

# Create the plot
fig, ax = plt.subplots()
time_steps = np.linspace(1, 94, 94)
# Plot the RTT values
ax.plot(time_steps, rtt, label="RTT")

# Set the labels and title
ax.set_xlabel("Time")
ax.set_ylabel("RTT")
ax.set_title("TCP Reno Round Trip Time")

# Add a legend
ax.legend()

# Show the plot
plt.show()


