# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

r""".. _ref_vm13:

Cylindrical Shell Under Pressure
---------------------------------
Problem description:
 - A long cylindrical pressure vessel of mean diameter d and wall thickness t has closed
   ends and is subjected to an internal pressure P. Determine the axial stress
   :math:`\sigma_y` and the hoop stress :math:`\sigma_z` in the vessel at the
   midthickness of the wall.

Reference:
 - S. Timoshenko, Strength of Materials, Part I, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1955,
   pg. 45, article 11.
 - UGURAL AND FENSTER, ADV. STRENGTH AND APPL. ELAS., 1981.

Analysis type(s):
 - Static Analysis ``ANTYPE=0``

Element type(s):
 - 2-Node Finite Strain Axisymmetric Shell (SHELL208)

.. image:: ../_static/vm13_setup.png
   :width: 400
   :alt: VM13 Cylindrical Shell Problem Sketch

Material properties:
 - :math:`E = 30 \cdot 10^6 psi`
 - :math:`\mu = 0.3`

Geometric properties:
 - :math:`t = 1 in`
 - :math:`d = 120 in`

Loading:
 - :math:`P = 500 psi`

Analysis Assumptions and Modeling Notes:
 - An arbitrary axial length of 10 inches is selected.
   Nodal coupling is used in the radial direction. An axial
   force of 5654866.8 lb (:math:`(Pπd^2)/4`) is applied to
   simulate the closed-end effect.

"""
# sphinx_gallery_thumbnail_path = '_static/vm13_setup.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np

# Launch MAPDL with specified settings
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)

# Clear any existing database
mapdl.clear()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Run the /VERIFY command for VM13
mapdl.verify("vm13")

# Set the title of the analysis
mapdl.title("VM13 CYLINDRICAL SHELL UNDER PRESSURE")

# Enter the model creation preprocessor
mapdl.prep7(mute=True)

###############################################################################
# Define element type and section properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 2-Node Axisymmetric Shell element (SHELL208) and "SHELL" as section type.

mapdl.et(1, "SHELL208")  # Element type SHELL208
mapdl.sectype(1, "SHELL")  # Section type SHELL
mapdl.secdata(1)  # Define section data
mapdl.secnum(1)  # Assign section number

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6
# and Poisson's ratio of 0.3 is specified.

mapdl.mp("EX", 1, 30e6)
mapdl.mp("NUXY", 1, 0.3)

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

mapdl.n(1, 60)  # Node 1, 60 degrees
mapdl.n(2, 60, 10)  # Node 2, 60 degrees and 10 units in Z-direction

# Define element connectivity
mapdl.e(1, 2)  # Element 1 with nodes 1 and 2

###############################################################################
# Define coupling and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Couple the nodes #1 and 2 in radial direction (rotation around Z-axis).
# Fix UY displacement for node 1. Fix ROTZ (rotation around Z-axis) for node 2.
# Apply a concentrated force value of 5654866.8 lb in FY direction at node 2.
# Internal pressure of 500 psi is applied. Then exit prep7 processor.
#
# Effectively, this sets:
#  :math:`P = 500 psi`

mapdl.cp(1, "UX", 1, 2)  # Couple radial direction (rotation around Z-axis)
mapdl.d(1, "UY", "", "", "", "", "ROTZ")  # Fix UY displacement for node 1
mapdl.d(2, "ROTZ")  # Fix ROTZ (rotation around Z-axis) for node 2

mapdl.f(2, "FY", 5654866.8)  # Apply a concentrated force FY to node 2
mapdl.sfe(1, 1, "PRES", "", 500)  # Apply internal pressure of 500 psi to element 1

# Selects all entities
mapdl.allsel()
mapdl.eplot()

# Finish the pre-processing processor
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.

mapdl.slashsolu()
# Set the analysis type to STATIC
mapdl.antype("STATIC")
# Controls the solution printout
mapdl.outpr("ALL", 1)
# Solve the analysis
mapdl.solve()
# Finish the solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing and compute stress components.

mapdl.post1()

# Create element tables for stress components
mapdl.etable("STRS_Y", "S", "Y")
mapdl.etable("STRS_Z", "S", "Z")

# Retrieve element stresses from the element tables using *Get
stress_y = mapdl.get("STRSS_Y", "ELEM", 1, "ETAB", "STRS_Y")
stress_z = mapdl.get("STRSS_Z", "ELEM", 1, "ETAB", "STRS_Z")

# Fill the array with target values
Target_values = np.array([15000, 29749])

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

results = f"""
------------------- VM13 RESULTS COMPARISON ---------------------
   RESULT      |  TARGET     |   Mechanical APDL   |   RATIO
Stress, Y (psi)  {Target_values[0]:.5f}    {stress_y:.5f}       {abs(stress_y/Target_values[0]):.5f}
Stress, Z (psi)  {Target_values[1]:.5f}    {stress_z:.5f}       {abs(stress_z/Target_values[1]):.5f}
-----------------------------------------------------------------
"""
print(results)

###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Stop MAPDL.
# ~~~~~~~~~~~
mapdl.exit()
