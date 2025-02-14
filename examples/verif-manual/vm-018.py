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

r""".. _ref_vm18:

Out-of-Plane Bending of a Curved Bar
------------------------------------
Problem description:
 - A portion of a horizontal circular ring, built-in at A, is loaded by a vertical (Z)
   load F applied at the end B. The ring has a solid circular cross-section of diameter d.
   Determine the deflection :math:`\delta` at end B, the maximum bending
   stress :math:`\sigma_{Bend}` , and the maximum torsional shear stress τ.

Reference:
 - S. Timoshenko, Strength of Materials, Part I, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1955,
   pg. 412, eq. 241.

Analysis type(s):
 - Static Analysis ``ANTYPE=0``

Element type(s):
 - Elastic Curved Pipe Element (PIPE18)
 - 3-D 3 Node Pipe Element (PIPE289)

.. figure:: ../_static/vm18_setup1.png
    :align: center
    :width: 400
    :alt:  VM18 Curved Bar Problem Sketch

.. figure:: ../_static/vm18_setup2.png
    :align: center
    :width: 400
    :alt: VM18 Curved Bar Finite Element Model

Material properties:
 - :math:`E = 30 \cdot 10^6 psi`
 - :math:`\mu = 0.3`

Geometric properties:
 - :math:`r = 100 in`
 - :math:`d = 2 in`
 - :math:`\theta = 90°`

Loading:
 - :math:`F = 50 lb`

Analysis Assumptions and Modeling Notes:
 - Node 10 is arbitrarily located on the radius of curvature side of the element to define the
   plane of the elbow when PIPE18 elements are used. The wall thickness is set to half the diameter
   for a solid bar. Since the section has no hole in the middle, ovalization cannot occur and
   PIPE289 elements can be used to determine the deflection and stresses.

"""
# sphinx_gallery_thumbnail_path = '_static/vm18_setup1.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np
import pandas as pd

# Launch MAPDL with specified settings
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)

# Clear the existing database
mapdl.clear()

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the /VERIFY command
mapdl.run("/VERIFY,VM18")

# Set the title of the analysis
mapdl.title("VM18 OUT-OF-PLANE BENDING OF A CURVED BAR")

# Enter the model creation /Prep7 preprocessor
mapdl.prep7()

###############################################################################
# Define element type and real properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use Elastic Curved Pipe element (PIPE18) and set KEYOPT(6)=2 for printing member forces.
mapdl.et(1, "PIPE18", "", "", "", "", "", 2)

# Define geometry parameters (OD, wall thickness, radius) using "r" command (real constant)
mapdl.r(1, 2, 1, 100)

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6
# and Poisson's ratio NUXY of 0.3 is specified.
mapdl.mp("EX", 1, 30e6)
mapdl.mp("NUXY", 1, 0.3)

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

# Define nodes
mapdl.n(1, 100)
mapdl.n(2, "", 100)
mapdl.n(10)

# Define element
mapdl.e(1, 2, 10)

###############################################################################
# Define boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix all dofs at node 1. Specify nodal force F = -50 lb along Z direction at node 2.
# Then exit prep7 processor.

mapdl.d(1, "ALL")  # Define boundary conditions
mapdl.f(2, "FZ", -50)  # Define load

# Selects all entities
mapdl.allsel()
# Element plot
mapdl.eplot(vtk=False)

# Finish preprocessing processor
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Set the analysis type to STATIC
mapdl.antype("STATIC")

# Set output options
mapdl.outpr("BASIC", 1)

# Perform the solution
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute deflection and stress quantities.
mapdl.post1()

# Set the current results set to the last set to be read from result file
mapdl.set("LAST")

# Get displacement results at node 2 in the Z direction
def_z = mapdl.get("DEF", "NODE", 2, "U", "Z")

# Create an element table for bending stresses using ETABLE command
strs_ben = mapdl.etable("STRS_BEN", "NMISC", 91)

# Create an element table for shear stresses using ETABLE command
strs_shr = mapdl.etable("STRS_SHR", "LS", 4)

# Get bending stresses (ETAB: STRS_BEN) for element 1
strss_b = mapdl.get("STRSS_B", "ELEM", 1, "ETAB", "STRS_BEN")

# Get shear stresses (ETAB: STRS_SHR) for element 1
strss_t = mapdl.get("STRSS_T", "ELEM", 1, "ETAB", "STRS_SHR")

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_val = [-2.648, 6366, -3183]

# Fill result values
sim_res = [def_z, strss_b, strss_t]

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["Deflection (in)", "Stress_Bend (psi)", "Shear Stress (psi)"]

data = [target_val, sim_res, np.abs(target_val) / np.abs(sim_res)]

title = f"""

------------------- VM18 RESULTS COMPARISON ---------------------

PIPE18:
-------
"""

print(title)
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Clears the database without restarting.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.run("/CLEAR,NOSTART")

###############################################################################
# Set a new title for the analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.title("VM18 OUT-OF-PLANE BENDING OF A CURVED BAR Using PIPE289 ELEMENT MODEL")

###############################################################################
# Switches to the preprocessor (PREP7)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.prep7()

###############################################################################
# Define element type and section properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 3-D 3-Node Pipe element (PIPE289) and set KEYOPT(4)= 2 Thick pipe theory.
mapdl.et(1, "PIPE289", "", "", "", 2)
mapdl.sectype(1, "PIPE")  # Set section type PIPE
mapdl.secdata(2, 1, 16)  # Set section data (OD, wall thickness)

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6
# and Poisson's ratio NUXY of 0.3 is specified.
mapdl.mp("EX", 1, 30e6)
mapdl.mp("NUXY", 1, 0.3)

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

mapdl.csys(1)  # Set coordinate system to 1

mapdl.n(1, 100)  # Define nodes

# Generate additional nodes
mapdl.ngen(19, 1, 1, "", "", "", 5)

# Define element
mapdl.e(1, 3, 2)

# Generate additional elements from an existing pattern
mapdl.egen(9, 2, -1)

# Reset coordinate system to global
mapdl.csys(0)

###############################################################################
# Define boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix all dofs at node 1. Specify nodal force F = -50 lb along Z direction at node 19.
# Then exit prep7 processor.
mapdl.d(1, "ALL")
mapdl.f(19, "FZ", -50)

# Selects all entities
mapdl.allsel()
# Element plot
mapdl.eplot(vtk=False)

# exists pre-processing processor
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Set the analysis type to STATIC
mapdl.antype("STATIC")

# Set output options
mapdl.outpr("BASIC", 1)

# Perform the solution
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute deflection and stress quantities.
mapdl.post1()

# Set the current results set to the last set
mapdl.set("LAST")
mapdl.graphics("POWER")  # Set graphics mode to POWER
mapdl.eshape(1)  # Set element shape
mapdl.view(1, 1, 1, 1)  # Set view

# Get displacement results at node 19 in the Z direction
def_z = mapdl.get("DEF", "NODE", 19, "U", "Z")

# Create an element table for bending stresses using ETABLE command
strs_ben = mapdl.etable("STRS_BEN", "SMISC", 35)

# Get bending stresses (ETAB: STRS_BEN) for element 1 using ETABLE command
strss_b = mapdl.get("STRSS_B", "ELEM", 1, "ETAB", "STRS_BEN")

# for graphics displays
mapdl.show(option="REV")
# Plot elemtal solution values for SXY component
mapdl.plesol("S", "XY")
# Get minimum shear stress
shear_sxy = mapdl.get("SHEAR", "PLNSOL", 0, "MIN")
mapdl.show("close")

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_val = [-2.648, 6366, -3183]

# Fill result values
sim_res = [def_z, strss_b, shear_sxy]

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["Deflection (in)", "Stress_Bend (psi)", "Shear Stress (psi)"]

data = [target_val, sim_res, np.abs(target_val) / np.abs(sim_res)]

title = f"""

PIPE289:
--------
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
