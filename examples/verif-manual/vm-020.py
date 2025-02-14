# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

r""".. _ref_vm20:

Cylindrical Membrane Under Pressure
-----------------------------------
Problem description:
 - A long cylindrical membrane container of diameter d and wall thickness t is subjected to a
   uniform internal pressure P. Determine the axial stress :math:`\sigma_1` and the
   hoop stress :math:`\sigma_2` in the container. See VM13 for the problem sketch.

Reference:
 - S. Timoshenko, Strength of Materials, Part II, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1956,
   pg. 121, article 25.

Analysis type(s):
 - Static Analysis ``ANTYPE=0``

Element type(s):
 - 4-Node Finite Strain Shell Elements (SHELL181)

.. image:: ../_static/vm20_setup.png
   :width: 400
   :alt: VM20 Cylindrical Membrane Problem Sketch

Material properties:
 - :math:`E = 30 \cdot 10^6 psi`
 - :math:`\mu = 0.3`

Geometric properties:
 - :math:`d = 120 in`
 - :math:`t = 1 in`

Loading:
 - :math:`p = 500 psi`

Analysis Assumptions and Modeling Notes:
 - An arbitrary axial length is selected. Since the problem is axisymmetric, only a one element
   sector is needed. A small angle :math:`\theta` = 10° is used for approximating the circular
   boundary with a straight-sided element. Nodal coupling is used at the boundaries. An axial
   traction of 15,000 psi is applied to the edge of the element to simulate the closed-end effect.
   The internal pressure is applied as an equivalent negative pressure on the exterior (face 1)
   of the element.

"""
# sphinx_gallery_thumbnail_path = '_static/vm20_setup.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np
import pandas as pd

# Launch MAPDL with specified options
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)

# Clear the existing database
mapdl.clear()

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the VM20 verification
mapdl.run("/VERIFY,VM20")

# Set the analysis title
mapdl.title("VM20 CYLINDRICAL MEMBRANE UNDER PRESSURE")

# Enter the model creation /Prep7 preprocessor
mapdl.prep7()

###############################################################################
# Define element type and section properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 4-Node Structural Shell element (SHELL181) for finite strain membrane. Specify
# key option for membrane stiffness only via setting Keyopt(1)=1. Include full integration
# via setting Keyopt(3)=2.

mapdl.et(1, "SHELL181")  # Define element type as SHELL181
mapdl.keyopt(1, 1, 1)  # Set key option for membrane stiffness only
mapdl.keyopt(1, 3, 2)  # Set key option for full integration
mapdl.sectype(1, "SHELL")  # Section type SHELL
mapdl.secdata(1, 1)  # Define section data

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6
# and Poisson's ratio NUXY of 0.3 is specified.

mapdl.mp("EX", 1, 30e6)  # Define modulus of elasticity
mapdl.mp("NUXY", 1, 0.3)  # Define Poisson's ratio

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

mapdl.csys(1)  # Define cylindrical coordinate system

mapdl.n(1, 60)  # Define nodes

# Define additional node with translation
mapdl.n(2, 60, "", 10)

# Generate additional nodes from an existing pattern
mapdl.ngen(2, 2, 1, 2, 1, "", 10)

# Rotate nodal coordinate system to cylindrical
mapdl.nrotat("ALL")

# Define elements
mapdl.e(1, 2, 4, 3)

###############################################################################
# Define coupling and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply couplings and fix UZ displacement at specific node and UY displacement for all nodes.
# Specify axial traction= -15000 psi and internal pressure= -500 psi on elements uaing SFE command.
# Then exit prep7 processor.

mapdl.cp(1, "UX", 1, 2, 3, 4)  # Couple radial displacements
mapdl.cp(2, "UZ", 2, 4)  # Couple UZ displacements

mapdl.d(1, "UZ", "", "", 3, 2)  # Fix UZ displacement at specific node
mapdl.d("ALL", "UY")  # Fix UY displacement for all nodes

mapdl.sfe(1, 4, "PRES", "", -15000)  # Apply axial traction on elements
mapdl.sfe(1, 1, "PRES", "", -500)  # Apply internal pressure on elements

# Selects all entities
mapdl.allsel()
# Element plot
mapdl.eplot(background="w")

# Finish the preprocessing steps
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Set the analysis type to STATIC
mapdl.antype("STATIC")

mapdl.outpr("NSOL", 1)  # Output the nodal solution
mapdl.outpr("RSOL", 1)  # Output the result summary

# Perform the solution
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute stress quantities.
mapdl.post1()

# Get hoop stresses at node 1
strs_hop = mapdl.get("STRS_HOP", "NODE", 1, "S", 2)
# Get axial stresses at node 1
strs_ax = mapdl.get("STRS_AX", "NODE", 1, "S", 1)

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_stress = [15000, 29749]

# Fill result values
sim_res = [strs_hop, strs_ax]

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["Stress_1 (psi)", "Stress_2 (psi)"]

data = [target_stress, sim_res, np.abs(target_stress) / np.abs(sim_res)]

title = f"""

------------------- VM20 RESULTS COMPARISON ---------------------

"""
print(title)
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Stop MAPDL.
# ~~~~~~~~~~~
mapdl.exit()
