"""
Code to executed the first time in each techdemo which uses jupyter-execute directive.

It homogenize style and settings. If needed, you can change the configuration locally per plot.
"""

import warnings

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

warnings.filterwarnings("ignore")

# jupyterlab boilerplate setup
import plotly.graph_objects as go  # noqa: F401
import pyvista

pyvista.set_plot_theme("document")
pyvista.global_theme.background = "white"
pyvista.global_theme.font.size = 22
pyvista.global_theme.font.label_size = 22
pyvista.global_theme.font.title_size = 22
pyvista.global_theme.window_size = [400, 400]
pyvista.global_theme.axes.show = True
pyvista.global_theme.show_scalar_bar = True
pyvista.global_theme.return_cpos = False
pyvista.global_theme.trame.server_proxy_enabled = True

pyvista.set_jupyter_backend("html")

mytheme = pyvista.global_theme
