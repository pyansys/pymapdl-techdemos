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

r""".. _ref_vm295:

One Dimensional Terzaghi's Consolidation Problem with Permeability as Function of Depth
---------------------------------------------------------------------------------------
Problem description:
 - The test case is to simulate a one-dimensional Terzaghi's problem with permeability as a function
   of the soil depth. A pressure P is applied on the top surface of the soil with depth H and
   width W. The top surface of the soil is fully permeable and the permeability decreases linearly
   with depth. The excess pore water pressure for 0.1, 0.2, 0.3, 0.4, and 0.5 day is calculated and
   compared against the reference results obtained using the PIM method (Figure 5, pg. 5916).

Reference:
 - A POINT INTERPOLATION METHOD FOR SIMULATING DISSIPATION PROCESS
   OF CONSOLIDATION, J.G.WANG, G.R.LIU, Y.G.WU, COMPUTER METHODS
   IN APPLIED MECHANICS AND ENGINEERING 190 (2001),PG: 5907-5922

Analysis type(s):
 - Static Analysis ``ANTYPE=0``

Element type(s):
 - 2D 4-Node Coupled Pore-Pressure Element (CPT212)

.. image:: ../_static/vm295_setup.png
   :width: 100
   :alt: VM295 Problem Sketch

Material properties:
 - Youngs modulus, :math:`E = 4 \cdot 10^7 Pa`
 - Poissons ratio, :math:`\mu = 0.3`
 - Permeability value at bottom of the soil, :math:`fpx = 1.728 \cdot 10^-3 m/day`
 - Permeability value at the top of the soil = :math:`100 * fpx`

Geometric properties:
 - Height, :math:`H = 16 m`
 - Width, :math:`W = 1 m`

Loading:
 - Pressure, :math:`P = 1 \cdot 10^4 Pa`

Analysis Assumptions and Modeling Notes:
 - The soil is modeled using 2D CPT212 elements with plane strain element behavior.
   The UX degree of freedom for all nodes is constrained and the UY degree of freedom at the bottom
   of the soil is constrained. The pressure degree of freedom at the top edge is constrained to
   make it fully permeable. Linearly varying permeability of the soil is defined using the TB,PM
   material model. Static analysis is performed with an end time of 86400 seconds (1 day) and with
   stepped pressure loading P on the top edge of the soil. The excess water pore pressure at depth
   H = 6 m is computed for 0.1 (8640 s), 0.2 (17280 s), 0.3 (25920 s), 0.4 (34560 s), and
   0.5 days (43200 s) by interpolating the solution obtained at the nearest time points.

"""
# sphinx_gallery_thumbnail_path = '_static/vm295_setup.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np

# Launch MAPDL with specified options
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)
# Clear the current database
mapdl.clear()

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the /VERIFY command for VM295
mapdl.run("/VERIFY,VM295")

# Set the title of the analysis
mapdl.title(
    "VM295 1D TERZAGHI'S CONSOLIDATION PROBLEM WITH PERMEABILITY AS FUNCTION OF DEPTH"
)

# Entering the PREP7 environment in MAPDL
mapdl.prep7(mute=True)

# Set Parameters
day = 24 * 3600  # SECONDS IN ONE DAY
h = 16  # TOTAL DEPTH OF SOIL IN METERS
w = 1  # WIDTH OF SOIL IN METERS
pres = 1e4  # PRESSURE IN PA
ex = 4e7  # YOUNG'S MODULUS IN PA
tt = 1 * day

###############################################################################
# Define element type and properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 2D 4 NOode Coupled Pore Pressure Element (CPT212) and
# set PLANE STRAIN Formulation Keyopt(3)=2.

mapdl.et(1, "CPT212")
mapdl.keyopt(1, 12, 1)
mapdl.keyopt(1, 3, 2)

###############################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 4e7
# and Poisson's ratio of 0.3 is specified.

mapdl.mp("EX", 1, ex)
mapdl.mp("NUXY", 1, 0.3)

# Set parameters
fpx = 1.728e-3 / day / 1e4  # PERMEABILITY FROM REFERENCE
one = 1.0

# Define TB material properties
mapdl.tb("PM", 1, "", "", "PERM")  # DEFINING PERMEABILITY FOR THE SOIL
mapdl.tbfield("YCOR", 0)  # LOCATION Y = 0
mapdl.tbdata(1, fpx, fpx, fpx)  # PERMEABILITY VALUES AT LOCATION Y=0
mapdl.tbfield("YCOR", h)  # LOCATION Y=16
# PERMEABILITY VALUES AT LOCATION Y=16, LINEAR VARIABLE PERMEABILITY
mapdl.tbdata(1, fpx * 100, fpx * 100, fpx * 100)
mapdl.tb("PM", 1, "", "", "BIOT")  # DEFINING BIOT COEFFICINET FOR SOIL
mapdl.tbdata(1, one)  # BIOT COEFFICIENT

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

mapdl.rectng(0, w, 0, h)  # Generate rectangle
# Specifies the divisions and spacing ratio on unmeshed lines
mapdl.lesize(4, "", "", 16)
mapdl.lesize(3, "", "", 1)
# For elements that support multiple shapes, specifies the element shape, set mshape=2D
mapdl.mshape(0, "2D")
mapdl.mshkey(1)  # Key(1) = Specifies mapped meshing should be used to mesh
mapdl.amesh(1)  # CREATING CPT212 ELEMENTS

###############################################################################
# Define boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix UX degrees of freedom. Constraining UY DOF AT Location Y=0.
# Defining the top portion of the soil as permeable.
# Then exit prep7 processor.

mapdl.d("ALL", "UX", 0)  # CONSTRAINING ALL UX DOF

mapdl.nsel("S", "LOC", "Y", 0)
mapdl.d("ALL", "UY", 0)  # CONSTRAINING UY DOF AT LOCATION Y=0
mapdl.nsel("ALL")

mapdl.nsel("S", "LOC", "Y", h)
mapdl.d("ALL", "PRES", 0)  # DEFINING THE TOP PORTION OF SOIL AS PERMEABLE
# selects all nodes
mapdl.nsel("ALL")
# selects all element
mapdl.esel("ALL")
mapdl.aplot()

# Finish pre-processing processor
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

mapdl.antype("STATIC")  # Performing static analysis
mapdl.nropt("UNSYM")  # UNSYMMETRIC NEWTON RAPHSON OPTION
mapdl.time(tt)  # END TIME

mapdl.nsel("S", "LOC", "Y", h)
# APPLYING Surface PRESSURE LOAD AT TOP OF THE SOIL
mapdl.sf("ALL", "PRES", pres)
# selects all nodes
mapdl.nsel("ALL")

# Specify number of SUBSTEPS
mapdl.nsubst(nsbstp=350, nsbmx=1000, nsbmn=150)

# Controls the solution data written to the database.
mapdl.outres("ALL", "ALL")
mapdl.kbc(1)  # STEPPED LOADING

# SOLVE STATIC ANALYSIS
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing.

mapdl.post1()
# Set the current results set to the last set to be read from result file
mapdl.set("LAST")
# redirects output to the default system output file
mapdl.run("/OUT")
# reactivates suppressed printout
mapdl.gopr()

###############################################################################
# Specify Reference Solution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.com("")
mapdl.com("EXCESS PORE PRESSURE IN KILOPASCALS AT LOCATION X=1,Y=6")
mapdl.com("FOR 0.1 DAY (8640 SECONDS),0.2 DAY (17280 SECONDS)")
mapdl.com("0.3 DAY (25920 SECONDS), 0.4 DAY (34560 SECONDS)")
mapdl.com("AND 0.5 DAY (43200 SECONDS) ARE COMPUTED AND COMPARED")
mapdl.com("AGAINST REFERENCE SOLUTION")
mapdl.com("")

###############################################################################
# Inline functions in PyMAPDL to query node
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
q = mapdl.queries
nd1 = q.node(1.0, 6.0, 0.0)

###############################################################################
# Post-processing: Compute pore pressure
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# redirects solver output to a file named "SCRATCH"
mapdl.run("/OUT,SCRATCH")
# Specify load set to read from the result file, load step =1, sub-step=16
mapdl.set(1, 16)
p11 = mapdl.get("P11", "NODE", nd1, "PRES")
t11 = mapdl.get("T11", "ACTIVE", 0, "SET", "TIME")
# Specify load set to read from the result file, load step =1, sub-step=17
mapdl.set(1, 17)
p12 = mapdl.get("P12", "NODE", nd1, "PRES")
t12 = mapdl.get("T12", "ACTIVE", 0, "SET", "TIME")
t1 = day * 0.1
mapdl.com("")
mapdl.com("INTERPOLATE THE RESULTS AT LOCATION (1,6,0) FOR TIME=0.1DAY")
mapdl.com("")
pt1 = (p11 + (t1 - t11) / (t12 - t11) * (p12 - p11)) / 1e3
# Specify load set to read from the result file, load step =1, sub-step=31
mapdl.set(1, 31)
p21 = mapdl.get("P21", "NODE", nd1, "PRES")
t21 = mapdl.get("T21", "ACTIVE", 0, "SET", "TIME")
# Specify load set to read from the result file, load step =1, sub-step=32
mapdl.set(1, 32)
p22 = mapdl.get("P22", "NODE", nd1, "PRES")
t22 = mapdl.get("T22", "ACTIVE", 0, "SET", "TIME")
t2 = day * 0.2
mapdl.com("")
mapdl.com("INTERPOLATE THE RESULTS AT LOCATION (1,6,0) FOR TIME=0.2DAY")
mapdl.com("")
pt2 = (p21 + (t2 - t21) / (t22 - t21) * (p22 - p21)) / 1e3
# Specify load set to read from the result file, load step =1, sub-step=46
mapdl.set(1, 46)
p31 = mapdl.get("P31", "NODE", nd1, "PRES")
t31 = mapdl.get("T31", "ACTIVE", 0, "SET", "TIME")
# Specify load set to read from the result file, load step =1, sub-step=47
mapdl.set(1, 47)
p32 = mapdl.get("P32", "NODE", nd1, "PRES")
t32 = mapdl.get("T32", "ACTIVE", 0, "SET", "TIME")
t3 = day * 0.3
mapdl.com("")
mapdl.com("INTERPOLATE THE RESULTS AT LOCATION (1,6,0) FOR TIME=0.3DAY")
mapdl.com("")
pt3 = (p31 + (t3 - t31) / (t32 - t31) * (p32 - p31)) / 1e3
# Specify load set to read from the result file, load step =1, sub-step=61
mapdl.set(1, 61)
p41 = mapdl.get("P41", "NODE", nd1, "PRES")
t41 = mapdl.get("T41", "ACTIVE", 0, "SET", "TIME")
# Specify load set to read from the result file, load step =1, sub-step=62
mapdl.set(1, 62)
p42 = mapdl.get("P42", "NODE", nd1, "PRES")
t42 = mapdl.get("T42", "ACTIVE", 0, "SET", "TIME")
t4 = day * 0.4
mapdl.com("")
mapdl.com("INTERPOLATE THE RESULTS AT LOCATION (1,6,0) FOR TIME=0.4DAY")
mapdl.com("")
pt4 = (p41 + (t4 - t41) / (t42 - t41) * (p42 - p41)) / 1e3
# Specify load set to read from the result file, load step =1, sub-step=76
mapdl.set(1, 76)
p51 = mapdl.get("P51", "NODE", nd1, "PRES")
t51 = mapdl.get("T51", "ACTIVE", 0, "SET", "TIME")
# Specify load set to read from the result file, load step =1, sub-step=77
mapdl.set(1, 77)
p52 = mapdl.get("P52", "NODE", nd1, "PRES")
t52 = mapdl.get("T52", "ACTIVE", 0, "SET", "TIME")
t5 = day * 0.5
mapdl.com("")
mapdl.com("INTERPOLATE THE RESULTS AT LOCATION (1,6,0) FOR TIME=0.5DAY")
mapdl.com("")
pt5 = (p51 + (t5 - t51) / (t52 - t51) * (p52 - p51)) / 1e3
# Store result values in array
P = np.array([pt1, pt2, pt3, pt4, pt5])

# REFERENCE RESULTS, FIGURE 5, PG 5916
# Fill the Target Result Values in array
Target_CP = np.array([5.230, 2.970, 1.769, 1.043, 0.632])

# store ratio
RT = []
for i in range(len(Target_CP)):
    a = P[i] / Target_CP[i]
    RT.append(a)

# assign labels for days
label = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

message = f"""
------------------- VM295 RESULTS COMPARISON ---------------------
   Time (day)  |  TARGET (kPa)    |   Mechanical APDL  |   RATIO
-----------------------------------------------------------------
"""
print(message)

for i in range(len(Target_CP)):
    message = f"""
    {label[i]:.5f}        {Target_CP[i]:.5f}              {P[i]:.5f}          {RT[i]:.5f}
    """
    print(message)

message = f"""
-----------------------------------------------------------------
"""
print(message)

###############################################################################
# Finish the post-processing processor.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.finish()

###############################################################################
# Stop MAPDL.
# ~~~~~~~~~~~
mapdl.exit()
