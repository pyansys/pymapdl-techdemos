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

r""".. _ref_vm25:

Stresses in a Long Cylinder
---------------------------
Problem description:
 - A long thick-walled cylinder is initially subjected to an internal pressure p.
   Determine the radial displacement :math:`\delta_r` at the inner surface, the
   radial stress :math:`\sigma_r` , and tangential stress :math:`\sigma_t` , at the
   inner and outer surfaces and at the middle wall thickness. Internal pressure is then
   removed and the cylinder is subjected to a rotation ω about its center line. Determine
   the radial :math:`\sigma_r` and tangential :math:`\sigma_t` stresses at the inner wall
   and at an interior point located at r = Xi.

Reference:
 - S. Timoshenko, Strength of Materials, Part II, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1956,
   pg. 213, problem 1 and pg. 213, article 42.

Analysis type(s):
 - Static Analysis ``ANTYPE=0``

Element type(s):
 - 2-D 8-Node Structural Solid Elements (PLANE183)

.. image:: ../_static/vm25_setup.png
   :width: 400
   :alt: VM25 Long Cylinder Problem Sketch

Material properties:
 - :math:`E = 30 \cdot 10^6 psi`
 - :math:`\mu = 0.3`
 - :math:`\rho = 0.00073 lb-sec^2/in^4`

Geometric properties:
 - :math:`a = 4 inches`
 - :math:`b = 8 inches`
 - :math:`X_i = 5.43 inches`

Loading:
 - :math:`p = 30,000 psi`
 - :math:`\Omega = 1000 rad/sec`

Analysis Assumptions and Modeling Notes:
 - The axial length is arbitrarily selected. Elements are oriented such that surface stresses
   may be obtained at the inner and outer cylinder surfaces.
   POST1 is used to display linearized stresses through the thickness of the cylinder when it is
   subjected to an internal pressure.

"""
# sphinx_gallery_thumbnail_path = '_static/vm25_setup.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np
import pandas as pd

# Launching MAPDL with specified settings
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)

# Clearing the MAPDL database
mapdl.clear()

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the /VERIFY command for VM25
mapdl.run("/VERIFY,VM25")

# Set the title of the analysis
mapdl.title("VM25 Stresses in a Long Cylinder")

# Enter the model creation /Prep7 preprocessor
mapdl.prep7()

# Deactivate automatic (smart) element sizing
mapdl.smrtsize(sizlvl="OFF")

###############################################################################
# Define element type and properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 2-D 8-Node or 6-Node Structural Solid and specify Axisymmetric element behavior
# via setting Keyopt(3)=1.
mapdl.et(1, "PLANE183", "", "", 1)

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6,
# Density, rho = 0.00073 and Poisson's ratio NUXY of 0.3 is specified.
mapdl.mp("EX", 1, 30e6)
mapdl.mp("DENS", 1, 0.00073)
mapdl.mp("NUXY", 1, 0.3)

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

# Defining node 1 with coordinates (4)
mapdl.n(1, 4)
# Defining node 2 with coordinates (4+4/14)
mapdl.n(2, "4+4/14")
# Defining node 3 with coordinates (4+4/14, 0.5)
mapdl.n(3, "4+4/14", 0.5)
# Defining node 4 with coordinates (4, 0.5)
mapdl.n(4, 4, 0.5)
# Defining node 5 with coordinates (4+4/28)
mapdl.n(5, "4+4/28")
# Defining node 6 with coordinates (4+4/14, 0.25)
mapdl.n(6, "4+4/14", 0.25)
# Defining node 7 with coordinates (4+4/28, 0.5)
mapdl.n(7, "4+4/28", 0.5)
# Defining node 8 with coordinates (4, 0.25)
mapdl.n(8, 4, 0.25)
# Creating element 1 with nodes 2, 3, 4, 5, 6, 7, and 8
mapdl.e(1, 2, 3, 4, 5, 6, 7, 8)

# Generating additional nodes along element 14 using the specified
# parameters (from an existing pattern)
mapdl.egen(14, 8, 1, "", "", "", "", "", "", "", "4/14")
# Merging nodes based on their coordinates
mapdl.nummrg("NODE")
# Generate a mesh using EGEN command
mapdl.egen(2, 111, 1, 14, "", "", "", "", "", "", "", 0.5)
# Merge the nodes that share the same coordinates
mapdl.nummrg("NODE")

###############################################################################
# Define coupling and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply a displacement boundary condition in the vertical direction (UY) to all nodes.
# Couple the axial displacements at the unconstrained Y-dir. Apply internal pressure of
# 30000 psi is applied on nodes. Also, apply dummy pressure for surface printout.
# Then exit prep7 processor.

mapdl.nsel("S", "LOC", "Y", 0)  # Select nodes located on the Y-axis
# Apply a displacement boundary condition
mapdl.d("ALL", "UY")
mapdl.nsel("S", "LOC", "Y", 1)  # Select nodes located on the positive Y-axis
# Couple the axial displacements at the unconstrained Y-dir
mapdl.cp(1, "UY", "ALL")

mapdl.nsel(
    "S", "LOC", "X", 4
)  # Select nodes located on the X-axis at a specific coordinate
# Apply internal pressure on nodes
mapdl.sf("", "PRES", 30000)

mapdl.nsel(
    "S", "LOC", "X", 8
)  # Select nodes located on the X-axis at a different coordinate
# Apply dummy pressure for surface printout
mapdl.sf("", "PRES", 1e-10)

# Selects all entities
mapdl.allsel()
# Element plot
mapdl.eplot(background="w")

# Finish the pre-processing processor
mapdl.finish()

# Save the finite element model
mapdl.save("MODEL")

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Set the analysis type to STATIC
mapdl.antype("STATIC")
# Output results for all nodes
mapdl.outpr("", "ALL")
# Perform the solution for the load step 1, which is the internal pressure
mapdl.solve()
# exists solution processor for load case 1
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute displacement and stress components.
mapdl.post1()

# Set the load step 1 and substep to 1
mapdl.set(1, 1)

###############################################################################
# Inline functions in PyMAPDL to query node
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
q = mapdl.queries
LFT_NODE = q.node(4, 0, 0)  # store node number to 'LFT_NODE' with coordinate (4,0,0)
MID_NODE = q.node(6, 0, 0)  # store node number to 'MID_NODE' with coordinate (6,0,0)
RT_NODE = q.node(8, 0, 0)  # store node number to 'RT_NODE' with coordinate (8,0,0)

###############################################################################
# Retrieve nodal deflection and section stresses
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Retrieves the displacement "DEF_4" of nodes associated to
# "LFT_NODE" in the X direction
def_4 = mapdl.get("DEF_4", "NODE", LFT_NODE, "U", "X")

# Retrieves the stress and store it "parm" of nodes associated to a
# variables 'LFT_NODE','MID_NODE' and 'RT_NODE'
rst_4_c1 = mapdl.get("RST_4_C1", "NODE", LFT_NODE, "S", "X")
rst_6_c1 = mapdl.get("RST_6_C1", "NODE", MID_NODE, "S", "X")
rst_8_c1 = mapdl.get("RST_8_C1", "NODE", RT_NODE, "S", "X")
tst_4_c1 = mapdl.get("TST_4_C1", "NODE", LFT_NODE, "S", "Z")
tst_6_c1 = mapdl.get("TST_6_C1", "NODE", MID_NODE, "S", "Z")
tst_8_c1 = mapdl.get("TST_8_C1", "NODE", RT_NODE, "S", "Z")

# Print the nodal stress solution (COMP means all stress components)
mapdl.prnsol("S", "COMP")

# Define a path with the name 'STRESS' and ID 2, no limits specified
mapdl.path("STRESS", 2, "", 48)
mapdl.ppath(1, LFT_NODE)  # Define the path points using the variable 'LFT_NODE'
mapdl.ppath(2, RT_NODE)  # Define the path points using the variable 'RT_NODE'
mapdl.plsect("S", "Z", -1)  # Display the SZ stresses in a sectional plot
mapdl.plsect("S", "X", -1)  # Display the SX stresses in a sectional plot
mapdl.prsect(-1)  # Print linearized stresses

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_def = 0.0078666
target_strss = [-30000, -7778, 0]
target_tst_strss = [50000, 27778, 20000]

# Fill result values
res_def = def_4
res_strss = [rst_4_c1, rst_6_c1, rst_8_c1]
res_tst_strss = [tst_4_c1, tst_6_c1, tst_8_c1]

title = f"""

------------------- VM25 RESULTS COMPARISON ---------------------

RESULTS FOR CASE p = 30,000 psi:
--------------------------------

"""

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["Displacement, in (r = 4 in)"]
data = [
    [target_def, res_def, abs(target_def / res_def)],
]
print(title)
print(pd.DataFrame(data, row_headers, col_headers))

# Radial stress results comparison
row_headers = [
    "Stress_r, psi (r = 4 in)",
    "Stress_r, psi (r = 6 in)",
    "Stress_r, psi (r = 8 in)",
]

data = [target_strss, res_strss, np.abs(target_strss) / np.abs(res_strss)]
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

# Tangential stress results comparison
row_headers = [
    "Stress_t, psi (r = 4 in)",
    "Stress_t, psi (r = 6 in)",
    "Stress_t, psi (r = 8 in)",
]
data = [
    target_tst_strss,
    res_tst_strss,
    np.abs(target_tst_strss) / np.abs(res_tst_strss),
]
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))


###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Set a new title for the analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.title("VM25 Stresses in a Long Cylinder - Rotation About Axis")

# Resume the Finite Element (FE) "MODEL" save previously
mapdl.resume("MODEL")

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Print all results
mapdl.outpr("", "ALL")

###############################################################################
# Define boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply a displacement boundary condition in the vertical direction (UY) to all nodes.
# Rotate the cylinder with an angular velocity of 1000 rad/sec. Also, apply dummy
# pressure for surface printout. Then exit solution processor.

mapdl.nsel(
    "S", "LOC", "Y", 0
)  # Select nodes located at Y=0 to prevent rigid body motion
mapdl.nsel("R", "LOC", "X", 4)  # Select nodes located at X=4
# Displace all nodes in the Y-direction
mapdl.d("ALL", "UY")

mapdl.nsel("S", "LOC", "X", 4)  # Select nodes located at X=4
# Apply a small pressure to allow stress printout
mapdl.sf("", "PRES", 1e-10)

mapdl.nsel("ALL")  # Select all nodes
# Rotate the cylinder with an angular velocity of 1000 RAD/SEC
mapdl.omega("", 1000)

# Solve the problem in load step 2 - centrifugal loading
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute displacement and stress components.
mapdl.post1()

###############################################################################
# Inline functions in PyMAPDL to query node
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
q = mapdl.queries
LFT_NODE = q.node(4, 0, 0)  # store node number to 'LFT_NODE' with coordinate (4,0,0)
XI_NODE = q.node(
    5.43, 0, 0
)  # store node number to 'XI_NODE' with coordinate (5.43,0,0)

###############################################################################
# Retrieve nodal deflection and section stresses
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rst_4_c2 = mapdl.get("RST_4_C2", "NODE", LFT_NODE, "S", "X")
tst_4_c2 = mapdl.get("TST_4_C2", "NODE", LFT_NODE, "S", "Z")
rst_x_c2 = mapdl.get("RST_X_C2", "NODE", XI_NODE, "S", "X")
tst_x_c2 = mapdl.get("TST_X_C2", "NODE", XI_NODE, "S", "Z")

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_strss = [0, 4753]
target_tst_strss = [40588, 29436]

# Fill result values
res_strss = [rst_4_c2, rst_x_c2]
res_tst_strss = [tst_4_c2, tst_x_c2]

title = f"""

RESULTS FOR CASE Rotation = 1000 rad/sec:
-----------------------------------------

"""

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]

# Radial stress results comparison
row_headers = ["Stress_r, psi (r = 4 in)", "Stress_r, psi (r = 5.43 in)"]

data = [target_strss, res_strss, np.abs(target_strss) / np.abs(res_strss)]

print(title)
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

# Tangential stress results comparison
row_headers = ["Stress_t, psi (r = 4 in)", "Stress_t, psi (r = 5.43 in)"]

data = [
    target_tst_strss,
    res_tst_strss,
    np.abs(target_tst_strss) / np.abs(res_tst_strss),
]
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Stop MAPDL.
# ~~~~~~~~~~~
mapdl.exit()
