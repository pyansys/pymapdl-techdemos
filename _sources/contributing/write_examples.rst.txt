How to write a good example?
============================

Here are some tips for writing a good example.

Use ``mapdl.convert_script``
----------------------------

If you want to translate a MAPDL script into a PyMAPDL one, you can first
run these commands:: 

    from ansys.mapdl.core import convert_script
    convert_script(path_MAPDL_script)

.. warning::

    The ``mapdl.convert_script`` method is still in the beta state. You should check its output.
    There may be easier ways to write some commands.

    For example, use ``mapdl.eplot()`` rather than ``mapdl.run("EPLOT")``.


Use Python packages as much as possible
---------------------------------------
The aim of PyMAPDL is to make it possible to create workflows that combine
MAPDL and the Python environment.
Some MAPDL workflows can be very efficient, but mixing them with Python packages
can simplify the code and allow you to generate more visually effective plots.

Do not hesitate to explore the `Python Package Index <pypi_org_>`_
to discover new Python packages.


Graphics and plots
------------------

The more visual your example is, the better.
Python facilitates the creation of sophisticate graphics and plots: take advantage
of that.

Packages like `Matplotlib <matplotlib_org_>`_, `Pandas <pandas_org_>`_
or `PyVista <pandas_org_>`_ can help you create nice graphics, tables, or plots .
