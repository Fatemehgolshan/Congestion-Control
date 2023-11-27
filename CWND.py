import matplotlib.pyplot as plt
import numpy as np

# Read the CWND and SSthresh values from the file
cwnd = []
ssthresh = []
with open("tcp_reno_simulation_50percent.cnwd-ssthresh", "r") as f:
    for line in f:
        try:
            cwnd_val, ssthresh_val = line.split()
            cwnd.append(float(cwnd_val))
            ssthresh.append(float(ssthresh_val))
        except ValueError:
            # Ignore lines that don't have two values
            pass

# Create the plot
fig, ax = plt.subplots()

# Plot the CWND and SSthresh values
ax.plot(cwnd, label="CWND")
ax.plot(ssthresh, label="SSThresh")
# Set the labels and title
ax.set_xlabel("Time")
ax.set_ylabel("CWND/SSThresh")
ax.set_title("Congestion Window and Slow Start Threshold")

# Add a legend
ax.legend()

# Show the plot
plt.show()

