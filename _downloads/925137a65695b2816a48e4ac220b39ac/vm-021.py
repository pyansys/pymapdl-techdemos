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

r""".. _ref_vm21:

Tie Rod with Lateral Loading
----------------------------
Problem description:
 - A tie rod is subjected to the action of a tensile force F and a uniform lateral load p.
   Determine the maximum deflection :math:`z_{max}`, the slope :math:`\theta` at the left-hand end,
   and the maximum bending moment :math:`M_{max}`. In addition, determine the same three quantities
   for the unstiffened tie rod (F = 0).

Reference:
 - S. Timoshenko, Strength of Materials, Part II, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1956,
   pg. 42, article 6.

Analysis type(s):
 - Static, Stress Stiffening Analysis ``ANTYPE=0``

Element type(s):
 - 3-D 2 node beam (BEAM188)

.. image:: ../_static/vm21_setup.png
   :width: 400
   :alt: VM21 Tie Rod Problem Sketch

Material properties:
 - :math:`E = 30 \cdot 10^6 psi`

Geometric properties:
 - :math:`l = 200 in`
 - :math:`b = h = 2.5 in`

Loading:
 - :math:`F = 21,972.6 lb`
 - :math:`p = 1.79253 lb/in`

Analysis Assumptions and Modeling Notes:
 - Due to symmetry, only one-half of the beam is modeled. The full load is applied for each
   iteration. The first solution represents the unstiffened case. The second solution represents
   the stiffened case.

"""
# sphinx_gallery_thumbnail_path = '_static/vm21_setup.png'

# Importing the `launch_mapdl` function from the `ansys.mapdl.core` module
from ansys.mapdl.core import launch_mapdl
import numpy as np
import pandas as pd

# Launch MAPDL with specified options
mapdl = launch_mapdl(loglevel="WARNING", print_com=True, remove_temp_dir_on_exit=True)

# Clear the current database
mapdl.clear()

# Run the FINISH command to exists normally from a processor
mapdl.finish()

# Set the ANSYS version
mapdl.com("ANSYS MEDIA REL. 2022R2 (05/13/2022) REF. VERIF. MANUAL: REL. 2022R2")

# Run the /VERIFY command for VM21
mapdl.run("/VERIFY,VM21")

# Set the title of the analysis
mapdl.title("VM21 TIE ROD WITH LATERAL LOADING NO STREES STIFFENING")

# Enter the model creation /Prep7 preprocessor
mapdl.prep7()

###############################################################################
# Define element type and section properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use 3-D 2-Node Beam Element and specify cubic shape function via setting Keyopt(3)=3.

mapdl.et(1, "BEAM188")

mapdl.keyopt(1, 3, 3)  # Set KEYOPT(3) to 3 cubic shape function
mapdl.sectype(1, "BEAM", "RECT")  # Specify section properties for the beam element
mapdl.secdata(2.5, 2.5)  # Define section data

##################################################################################
# Define material
# ~~~~~~~~~~~~~~~
# Set up the material and its type (a single material), Young's modulus of 30e6
# and Poisson's ratio PRXY of 0.3 is specified.

mapdl.mp("EX", 1, 30e6)
mapdl.mp("PRXY", "", 0.3)

###############################################################################
# Define geometry
# ~~~~~~~~~~~~~~~
# Set up the nodes and elements. This creates a mesh just like in the
# problem setup.

mapdl.n(1)  # define nodes
mapdl.n(5, 100)

# Generate additional nodes
mapdl.fill()

# Define elements
mapdl.e(1, 2)

# Generate additional elements from an existing pattern
mapdl.egen(4, 1, 1)

###############################################################################
# Define boundary conditions and loading
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply a displacement boundary condition in the UY, ROTX and ROTZ directions to all nodes.
# Specify symmetry degree-of-freedom constraints on nodes, surface normal to X-dir (default).
# Apply a tensile force in X-dir, F = -21972.6 lb and a uniform lateral load, p = 1.79253 lb/in.
# Then exit prep7 processor.

mapdl.d("ALL", "UY", "", "", "", "", "ROTX", "ROTZ")
mapdl.d(1, "UZ")

# Select nodes for symmetry boundary
mapdl.nsel("S", "", "", 5)
mapdl.dsym("SYMM", "X")

# Select all nodes
mapdl.nsel("ALL")

# Apply nodal force along x-direction
mapdl.f(1, "FX", -21972.6)
# Specifies surface loads on beam and pipe elements.
mapdl.sfbeam("ALL", 1, "PRES", 1.79253)

# Selects all entities
mapdl.allsel()
# Element plot
mapdl.eplot()

# Finish pre-processing processor
mapdl.finish()

###############################################################################
# Solve
# ~~~~~
# Enter solution mode and solve the system.
mapdl.slashsolu()

# Set the analysis type to STATIC
mapdl.antype("STATIC")
# Perform the solution
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute displacement and rotation quantities.
mapdl.post1()

# Select nodes for results output
mapdl.nsel("S", "", "", 1, 5, 4)

# Print displacement quantities in Z direction
mapdl.prnsol("U", "Z")

# Print rotation quantities in Y direction
mapdl.prnsol("ROT", "Y")

# Select all nodes
mapdl.nsel("ALL")

# Print results solution
mapdl.prrsol()

###############################################################################
# Inline functions in PyMAPDL to query node
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
q = mapdl.queries
RGHT_END = q.node(200, 0, 0)  # store node number to 'RGHT_END' with coordinate (4,0,0)
LFT_END = q.node(0, 0, 0)  # store node number to 'LFT_END' with coordinate (4,0,0)

###############################################################################
# Retrieve nodal deflection and rotation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get results at node RGHT_END
uz_mx_c2 = mapdl.get("UZ_MX_C2", "NODE", RGHT_END, "U", "Z")

# Get results at node LFT_END
slope_c2 = mapdl.get("SLOPE_C2", "NODE", LFT_END, "ROT", "Y")

# exists post-processing processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter /post26 time-history post-processing processor.
mapdl.post26()

# Specifies the total reaction force data to be stored at nodes associated to RGHT_END
mapdl.rforce(2, RGHT_END, "M", "Y")

# Store results
mapdl.store()
# Get maximum moment at node RGHT_END
m_mx_c2 = mapdl.get("M_MX_C2", "VARI", 2, "EXTREM", "VMAX")

# exists post-processing processor
mapdl.finish()

###############################################################################
# Set a new title for the analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mapdl.title("VM21 TIE ROD WITH LATERAL LOADING STRESS STIFFENING PRESENT")

###############################################################################
# Solve
# ~~~~~
# Enter new solution mode and solve the nonlinear system including stress stiffening.
mapdl.slashsolu()

# Set number of substeps to 5
mapdl.nsubst(5)
# Activate auto time stepping
mapdl.autots("ON")
# Activate nonlinear geometry
mapdl.nlgeom("ON")
# Set a smaller convergence tolerance
mapdl.cnvtol("F", "", 0.0001, "", 1)
# Perform the solution
mapdl.solve()
# exists solution processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter post-processing. Compute displacement and rotation quantities.
mapdl.post1()

# Select nodes for results output
mapdl.nsel("S", "", "", 1, 5, 4)
# Print displacement quantities in Z direction
mapdl.prnsol("U", "Z")
# Print rotation quantities in Y direction
mapdl.prnsol("ROT", "Y")
# Print results solution
mapdl.prrsol()

# Get results at node RGHT_END
uz_mx_c1 = mapdl.get("UZ_MX_C1", "NODE", RGHT_END, "U", "Z")

# Get results at node LFT_END
slope_c1 = mapdl.get("SLOPE_C1", "NODE", LFT_END, "ROT", "Y")

# exists post-processing processor
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~
# Enter /post26 time-history post-processing processor.
mapdl.post26()

# Specifies the total reaction force data to be stored at nodes associated to RGHT_END
mapdl.rforce(2, RGHT_END, "M", "Y")

# Store results
mapdl.store()

# Get maximum moment at node RGHT_END
m_mx_c1 = mapdl.get("M_MX_C1", "VARI", 2, "EXTREM", "VMAX")

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

# Set target values
target_res = [-0.19945, 0.0032352, -4580.1]
target_res_strss = [-0.38241, 0.0061185, -8962.7]

# Fill result values
sim_res = [uz_mx_c1, slope_c1, m_mx_c1]
sim_res_strss = [uz_mx_c2, slope_c2, m_mx_c2]

title = f"""

------------------- VM21 RESULTS COMPARISON ---------------------

F neq 0 (stiffened):
--------------------

"""

col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["Z_max, in", "Slope, rad", "M_max , in-lb"]

data = [target_res, sim_res, np.abs(target_res) / np.abs(sim_res)]

print(title)
print(pd.DataFrame(np.transpose(data), row_headers, col_headers))

title = f"""


F = 0 (unstiffened):
--------------------

"""

row_headers = ["Z_max, in", "Slope, rad", "M_max , in-lb"]
data = [
    target_res_strss,
    sim_res_strss,
    np.abs(target_res_strss) / np.abs(sim_res_strss),
]

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
