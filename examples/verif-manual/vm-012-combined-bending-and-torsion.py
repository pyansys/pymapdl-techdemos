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

r""".. _ref_vm12_example:

Combined bending and torsion
----------------------------
Problem description:
 - A vertical bar of length :math:`l` is subjected to the action of a
   horizontal force F acting at a distance d from the axis of the bar.
   Determine the maximum principal stress :math:`\sigma _{max}` and the
   maximum shear stress :math:`\tau _ {max}` in the bar.

Reference:
 - Timoshenko, Strength of Materials, Part I, Elementary Theory and
   Problems, 3rd Edition, D. Van Nostrand Co., Inc., New York, NY, 1955,
   pg. 299, problem 2.

Analysis type(s):
 - Static analysis ``ANTYPE=0``

Element type(s):
 - Elastic straight pipe element (``PIPE16``)
 - 3D 2 Node pipe element (``PIPE288``)

.. image:: ../_static/vm12_setup.png
   :width: 400
   :alt: VM12 Problem Sketch

Material properties
 - :math:`E = 30 \cdot 10^6 psi`
 - :math:`u=0.3`

Geometric properties:
 - :math:`l = 25 l`
 - :math:`d = 3 ft`
 - Section modulus :math:`(l/c) = 10 in^3`
 - Outer Diameter :math:`= 4.67017 in`
 - Wall Thickness :math:`= 2.33508 in`

Loading:
 - :math:`F = 250 lb`
 - :math:`M = Fd = 9000 in-lb`

Analysis assumptions and modeling notes:
 - Use consistent length units of inches. Real constants for PIPE16 and
   section properties for PIPE288 are used to define the pipe Outer Diameter
   and Wall Thickness. These values are calculated for a solid cross-section
   from the given section modulus. The offset load is applied as a centroidal
   force and a moment.

"""
# sphinx_gallery_thumbnail_path = '_static/vm12_setup.png'

from ansys.mapdl.core import launch_mapdl
import pandas

###############################################################################
# Start MAPDL
# ~~~~~~~~~~~
# Start MAPDL.
mapdl = launch_mapdl(loglevel="WARNING", print_com=True)
mapdl.clear()  # optional as MAPDL just started

###############################################################################
# Pre-processing with ET PIPE16
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mapdl.verify("vm12")
mapdl.prep7()

mapdl.antype("STATIC")
mapdl.et(1, "PIPE16")
mapdl.r(1, 4.67017, 2.33508)  # REAL CONSTANTS FOR SOLID CROSS SECTION
mapdl.mp("EX", 1, 30e6)
mapdl.mp("NUXY", 1, 0.3)
mapdl.n(1)
mapdl.n(2, "", "", 300)
mapdl.e(1, 2)
mapdl.d(1, "ALL")
mapdl.f(2, "MZ", 9000)
mapdl.f(2, "FX", -250)
mapdl.finish()

###############################################################################
# Solve
# ~~~~~

mapdl.slashsolu()
mapdl.outpr("BASIC", 1)

mapdl.solve()
mapdl.finish()
mapdl.post1()
mapdl.etable("P_STRS", "NMISC", 86)
mapdl.etable("SHR", "NMISC", 88)


###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~

p_stress = mapdl.get("P_STRESS", "ELEM", 1, "ETAB", "P_STRS")
shear = mapdl.get("SHEAR", "ELEM", 1, "ETAB", "SHR")
p_trs = shear / 2

# Fill the array with target values
target_p_stress = 7527
target_p_trs = 3777

data = [
    [target_p_stress, p_stress, abs(p_stress / target_p_stress)],
    [target_p_trs, p_trs, abs(p_trs / target_p_trs)],
]
col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["MAX PRINSTRS psi", "MAX SH STRS psi"]

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

print(pandas.DataFrame(data, row_headers, col_headers))


###############################################################################
# Pre-processing with ET PIPE288
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mapdl.clear("nostart")
mapdl.prep7()
mapdl.run("C***     USING PIPE288")
mapdl.antype("STATIC")
mapdl.et(1, "PIPE288", "", "", "", 2)
mapdl.sectype(1, "PIPE")
mapdl.secdata(4.67017, 2.33508)
mapdl.keyopt(1, 3, 3)  # CUBIC SHAPE FUNCTION
mapdl.mp("EX", 1, 30e6)
mapdl.mp("NUXY", 1, 0.3)
mapdl.n(1)
mapdl.n(2, "", "", 300)
mapdl.e(1, 2)
mapdl.d(1, "ALL")
mapdl.f(2, "MZ", 9000)
mapdl.f(2, "FX", -250)
mapdl.finish()

mapdl.allsel()
mapdl.eplot()


###############################################################################
# Solve
# ~~~~~

mapdl.slashsolu()
mapdl.outpr("BASIC", 1)
mapdl.solve()
mapdl.finish()

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~

mapdl.post1()
mapdl.set("LAST")
mapdl.graphics("POWER")
mapdl.eshape(1)
mapdl.view(1, 1, 1, 1)

mapdl.show(option="REV", fname="png")
mapdl.plesol("S", 1)
mapdl.show("close")

p_stress = mapdl.get("P_STRESS", "PLNSOL", 0, "MAX")

mapdl.show(option="REV", fname="png")
mapdl.plesol("S", "INT")
mapdl.show("close")

shear = mapdl.get("SHEAR", "PLNSOL", 0, "MAX")
p_trs = shear / 2


# Fill the array with target values
target_p_stress = 7527.0
target_p_trs = 3777.0

data = [
    [target_p_stress, p_stress, abs(p_stress / target_p_stress)],
    [target_p_trs, p_trs, abs(p_trs / target_p_trs)],
]
col_headers = ["TARGET", "Mechanical APDL", "RATIO"]
row_headers = ["MAX PRINSTRS psi", "MAX SH STRS psi"]

###############################################################################
# Verify the results.
# ~~~~~~~~~~~~~~~~~~~

print(pandas.DataFrame(data, row_headers, col_headers))

mapdl.finish()
mapdl.starlist("vm12", "vrt")

###############################################################################
# Stop MAPDL.
mapdl.exit()
