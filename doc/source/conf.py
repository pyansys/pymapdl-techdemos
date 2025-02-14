"""Sphinx documentation configuration file."""
from datetime import datetime
import os

from ansys.mapdl import core as pymapdl
from ansys_sphinx_theme import ansys_favicon
from ansys_sphinx_theme import pyansys_logo_black as logo
import numpy as np
import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx_gallery.sorting import FileNameSortKey

# Project information
project = "pymapdl-examples"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = "0.1.dev0"

REPOSITORY_NAME = "pymapdl-examples"
USERNAME = "ansys"
BRANCH = "main"
DOC_PATH = "doc/source"

# Select desired logo, theme, and declare the html title
html_logo = logo
html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyMAPDL Examples"


# necessary when building the sphinx gallery
pymapdl.BUILDING_GALLERY = True
pyvista.BUILDING_GALLERY = True
pyvista.OFF_SCREEN = True

# specify the location of your github repo
html_theme_options = {
    "github_url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}",
    "show_prev_next": False,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyMAPDL", "https://mapdl.docs.pyansys.com/"),
        ("Examples", "https://mapdl.docs.pyansys.com/version/stable/examples/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": f"https://github.com/{USERNAME}/{REPOSITORY_NAME}/discussions",
            "icon": "fa fa-comment fa-fw",
        },
    ],
}

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": USERNAME,
    "github_repo": REPOSITORY_NAME,
    "github_version": BRANCH,
    "doc_path": DOC_PATH,
}

# Sphinx extensions
extensions = [
    "jupyter_sphinx",
    "notfound.extension",
    "numpydoc",
    "pyvista.ext.viewer_directive",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_design",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinxemoji.sphinxemoji",
]

# -- Sphinx Gallery Options ---------------------------------------------------
sphinx_gallery_conf = {
    # convert rst to md for ipynb
    "pypandoc": True,
    # path to your examples scripts
    "examples_dirs": ["../../examples/verif-manual"],
    # path where to save gallery generated examples
    "gallery_dirs": ["verif-manual"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created. In
    "doc_module": "ansys-mapdl-core",
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "ignore_pattern": "flycheck*",
    "thumbnail_size": (350, 350),
}

suppress_warnings = ["config.cache"]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
numpydoc_xref_param_type = True

# Image referencing
numfig = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Manage errors
pyvista.set_error_output_file("errors.txt")


# must be less than or equal to the XVFB window size
try:
    pyvista.global_theme.window_size = np.array([1024, 768])
except AttributeError:
    # for compatibility with pyvista < 0.40
    pyvista.rcParams["window_size"] = np.array([1024, 768])

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# Executing theming
with open("common_jupyter_execute.py") as f:
    exec(f.read())

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "links.rst",
]

# make rst_epilog a variable, so you can add other epilog parts to it
rst_epilog = ""
# Read link all targets from file
with open("links.rst") as f:
    rst_epilog += f.read()

# ignore some link checks
linkcheck_ignore = [
    "https://ansyshelp.ansys.com/*",
]
