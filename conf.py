# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import re

# -- Project information -----------------------------------------------------

project = 'Open MPI'
copyright = '2020, The Open MPI Community'
author = 'The Open MPI Community'

# The full version, including alpha/beta/rc tags
# Read the Open MPI version from the VERSION file
with open("../VERSION") as fp:
    ompi_lines = fp.readlines()

ompi_data = dict()
for ompi_line in ompi_lines:
    if '#' in ompi_line:
        ompi_line, _ = ompi_line.split("#")
    ompi_line = ompi_line.strip()

    if '=' not in ompi_line:
        continue

    ompi_key, ompi_val = ompi_line.split("=")
    ompi_data[ompi_key.strip()] = ompi_val.strip()

# Release is a sphinx config variable -- assign it to the computed
# Open MPI version number.
series = f"{ompi_data['major']}.{ompi_data['minor']}.x"
release = f"{ompi_data['major']}.{ompi_data['minor']}.{ompi_data['release']}{ompi_data['greek']}"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
import sphinx_rtd_theme
extensions = ['recommonmark', "sphinx_rtd_theme"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
html_static_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'venv', 'py*/**']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']
html_static_path = []

# -- Options for MAN output -------------------------------------------------

def string_is_int(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

# This works
#man_pages=[("ompi/mpi/man/man3/MPI_Abort.3in","ompi/mpi/man/man3/MPI_Abort.3in","MPI_Abort.3in","",3)]

#man_make_section_directory='True'
import os
import glob
from pathlib import Path
man_pages=[]
for path in Path('./').rglob('*.rst'):
    sname=path.name
    vsname=re.sub('\.[0-9]*\.rst','',path.name)
    os.makedirs('../_build/man/' + str(path.parent),exist_ok = True)
    print('../_build/man/' + str(path.parent))
    snum=os.path.basename(os.path.dirname(path)).replace('man','')
    if string_is_int(snum):
      lname=(str(path.parent) + '/' + sname.replace('.rst',''))
      man_pages.append((lname,vsname,"","",int(snum)))

print(man_pages)

# -- Open MPI-specific options -----------------------------------------------

# This prolog is included in every file.  Put common stuff here.

rst_prolog = f"""
.. |mdash|  unicode:: U+02014 .. Em dash
.. |rarrow| unicode:: U+02192 .. Right arrow

.. |ompi_ver| replace:: {release}
.. |ompi_series| replace:: {series}
"""
