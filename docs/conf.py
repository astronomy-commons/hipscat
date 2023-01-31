# Configuration file for the Sphinx documentation builder.

import subprocess

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "HiPSCat"
copyright = "2023, astronomy-commons"
author = "astronomy-commons"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

# templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
# html_static_path = ["_static"]


# -- Options for Napoleon-------------------------------------------------
# Napoleon compiles the docstrings into .rst

# If True, include class __init__ docstrings separately from class
napoleon_include_init_with_doc = False
# If True, include docstrings of private functions
napoleon_include_private_with_doc = False
# Detail for converting docstrings to rst
napoleon_use_ivar = True

subprocess.run("cp source/index_body.rst index.rst", shell=True)
subprocess.run("cp source/api_body.rst api.rst", shell=True)
