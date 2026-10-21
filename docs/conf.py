# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# The package lives in src/ (src layout), so autodoc imports it from there.
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "T-TEA"
copyright = "2025-%Y, Udesc - Larva"
author = "Udesc - Larva"
release = "2.0.0"
language = "en"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# numpydoc formats the NumPy-style docstrings; napoleon is not needed and
# would only process the same docstrings a second time.
extensions = [
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc -----------------------------------------------------------------

# Show "CameraConfig" instead of the fully qualified name in headings.
add_module_names = False
# Keep members in the same order as in the source code.
autodoc_member_order = "bysource"
# Move type hints out of the signature into the parameter descriptions.
autodoc_typehints = "description"
# Hide the "Parameters" entries generated only from type hints when the
# docstring does not document them.
autodoc_typehints_description_target = "documented"

# -- Autosummary -------------------------------------------------------------

# Generate one page per package, module and class into docs/api/ (see
# modules.rst and _templates/autosummary/). Pages are rebuilt on every build.
autosummary_generate = True

# -- numpydoc ----------------------------------------------------------------

# Do not add an extra autosummary table of members to every class; autodoc
# already lists them.
numpydoc_show_class_members = False

# -- Intersphinx -------------------------------------------------------------

# Link types such as pathlib.Path, QWidget and numpy.ndarray to their
# official documentation (needs internet access during the build).
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "PySide6": ("https://doc.qt.io/qtforpython-6/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = f"{project} {release} documentation"
html_short_title = project

html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    # Theme default; the old "white" made the white project name invisible.
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": -1,
    "includehidden": True,
    "titles_only": False,
}
