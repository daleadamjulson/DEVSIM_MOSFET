import os
import numpy as np
import matplotlib.pyplot as plt

# --- List of paths to the directories where the .npz files are stored
directories = [
    "results"
]

titles = {0: "V$_d$ = 0.2V"}

plt.figure(figsize=(8, 6))

for i, dir_path in enumerate(directories):
    file_path = os.path.join(dir_path, "device_data.npz")
    data = np.load(file_path)
    print(data)

    drain_voltages = data["gate_voltages"]
    drain_currents_drain = data["drain_currents_gate"]

    plt.plot(drain_voltages, drain_currents_drain, label=f"{titles[i]}")

plt.xlabel("Gate Voltage (V)")
plt.ylabel("Drain Current (A)")
plt.title("Gate Voltage vs. Drain Current (Drain Terminal)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()