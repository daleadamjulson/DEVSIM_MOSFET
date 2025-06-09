# Copyright 2013 Devsim LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from devsim.python_packages.simple_physics import *
from devsim.python_packages.ramp import *
import devsim
import matplotlib.pyplot as plt
import numpy as np
import os

output_dir ="results"

os.makedirs(output_dir)

devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

device = "mos2d"

import gmsh_mos2d_create
gmsh_mos2d_create.load(device=device, infile="gmsh_mos2d.msh")

device = "mos2d"
silicon_regions=("gate", "bulk")
oxide_regions=("oxide",)
regions = ("gate", "bulk", "oxide")
interfaces = ("bulk_oxide", "gate_oxide")

for i in regions:
    CreateSolution(device, i, "Potential")

for i in silicon_regions:
    SetSiliconParameters(device, i, 300)
    CreateSiliconPotentialOnly(device, i)

for i in oxide_regions:
    SetOxideParameters(device, i, 300)
    CreateOxidePotentialOnly(device, i, "log_damp")

### Set up contacts
contacts = devsim.get_contact_list(device=device)
for i in contacts:
    tmp = devsim.get_region_list(device=device, contact=i)
    r = tmp[0]
    print("%s %s" % (r, i))
    CreateSiliconPotentialOnlyContact(device, r, i)
    devsim.set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

for i in interfaces:
    CreateSiliconOxideInterface(device, i)

devsim.solve(type="dc", absolute_error=1.0e-13, relative_error=1e-12, maximum_iterations=30)
devsim.solve(type="dc", absolute_error=1.0e-13, relative_error=1e-12, maximum_iterations=30)

for i in silicon_regions:
    CreateSolution(device, i, "Electrons")
    CreateSolution(device, i, "Holes")
    devsim.set_node_values(device=device, region=i, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=i, name="Holes",     init_from="IntrinsicHoles")
    CreateSiliconDriftDiffusion(device, i, "mu_n", "mu_p")

for c in contacts:
    tmp = devsim.get_region_list(device=device, contact=c)
    r = tmp[0]
    CreateSiliconDriftDiffusionAtContact(device, r, c)

devsim.solve(type="dc", absolute_error=1.0e30, relative_error=1e-5, maximum_iterations=30)

for r in silicon_regions:
    devsim.node_model(device=device, region=r, name="logElectrons", equation="log(Electrons)/log(10)")

for r in silicon_regions:
    devsim.element_from_edge_model(edge_model="ElectricField",   device=device, region=r)
    devsim.element_from_edge_model(edge_model="ElectronCurrent", device=device, region=r)
    devsim.element_from_edge_model(edge_model="HoleCurrent",     device=device, region=r)

gate_voltage = 5.0
drain_voltage = 0.2

print("BEGINNING INITIAL GATE RAMP...")
gate_results = rampbias(device, "gate",  -3.0, 0.01, 0.001, 100, 1e-8, 1e30, returnAllCurrents)
print(f"Gate results dict: {gate_results}")
print("ENDING GATE RAMP...")


print("BEGINNING DRAIN RAMP...")
drain_results = rampbias(device, "drain", drain_voltage, 0.01, 0.001, 100, 1e-8, 1e30, returnAllCurrents)
print(f"Drain results dict: {drain_results}")
print("ENDING DRAIN RAMP...")

# Extract voltage and current values
drain_voltages = []
drain_currents_drain = []
drain_currents_source = []

for v, current_dict in drain_results:
    drain_voltages.append(v)
    drain_currents_drain.append(current_dict["drain"])  # Only extract drain current
    drain_currents_source.append(current_dict["source"])

# Convert to numpy arrays if desired

drain_voltages = np.array(drain_voltages)
drain_currents_drain = np.array(drain_currents_drain)
drain_currents_source = np.array(drain_currents_source)

# Plotting
plt.figure(figsize=(6, 4))
plt.plot(drain_voltages, drain_currents_drain, marker='o', linestyle='-', color='b')
plt.xlabel("Drain Voltage (V)")
plt.ylabel("Drain Current (A)")
plt.title(f"I-V Curve at Gate Bias = {gate_voltage} V")
plt.grid(True)
plt.tight_layout()
plt.show()

print("BEGINNING INITIAL GATE RAMP...")
gate_results = rampbias(device, "gate",  gate_voltage, 0.01, 0.001, 100, 1e-8, 1e30, returnAllCurrents)
print(f"Gate results dict: {gate_results}")
print("ENDING GATE RAMP...")

# Extract voltage and current values
gate_voltages = []
drain_currents_gate = []

for v, current_dict in gate_results:
    gate_voltages.append(v)
    drain_currents_gate.append(current_dict["drain"])  # Only extract drain current

# Convert to numpy arrays if desired

gate_voltages = np.array(gate_voltages)
drain_currents_gate = np.array(drain_currents_gate)

# Plotting
plt.figure(figsize=(6, 4))
plt.plot(gate_voltages, drain_currents_gate, marker='o', linestyle='-', color='b')
plt.xlabel("Gate Voltage (V)")
plt.ylabel("Drain Current (A)")
plt.title(f"I-V Curve at Gate Bias = {gate_voltage} V")
plt.grid(True)
plt.tight_layout()
plt.show()

np.savez(f"{output_dir}/device_data.npz",
         gate_voltages=gate_voltages,
         drain_currents_gate=drain_currents_gate)

devsim.write_devices(file=f"{output_dir}/gmsh_mos2d_dd.dat", type="tecplot")

