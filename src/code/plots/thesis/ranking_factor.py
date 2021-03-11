import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":
    slots = 5
    rc = [0.0, 0.5, 1.0]

    fig, ax = plt.subplots()
    for r in rc:
        ax.plot([i for i in range(slots)], [np.exp((1.0 - j) * (r ** 2)) for j in range(slots)], label=f"r = {r}")
    ax.set_xlabel("Ranking Slot (i)", fontsize="large")
    ax.set_ylabel("$e^{(1-i) * r^{2}}$", fontsize="xx-large")
    ax.legend()

    plt.xticks(np.arange(0, slots, step=1))
    plt.show()
