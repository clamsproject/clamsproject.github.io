# Configuration file for the Sphinx documentation builder.
# CLAMS Project Documentation Hub

import os
import sys

# -- Project information -----------------------------------------------------
project = 'CLAMS'
copyright = '2025, Brandeis LLC'
author = 'Brandeis LLC'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    'sphinx.ext.autodoc',           # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',          # Support for NumPy/Google docstrings
    'sphinx.ext.viewcode',          # Add links to highlighted source code
    'sphinx.ext.intersphinx',       # Link between Sphinx documentations
    'sphinx_copybutton',            # Add copy button to code blocks
    'sphinx_design',                # Cards, grids, tabs components
    'sphinxcontrib.mermaid',        # Diagram support
    'myst_parser',                  # Markdown support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
# Using Furo for visual consistency across all CLAMS projects
html_theme = 'furo'

# Theme options
html_theme_options = {
    "light_logo": "clams-logo.png",
    "dark_logo": "clams-logo.png",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/clamsproject/clamsproject.github.io",
    "source_branch": "main",
    "source_directory": "documentation/",

    # Color scheme (matching current Jekyll theme)
    "light_css_variables": {
        "color-brand-primary": "#008AFF",
        "color-brand-content": "#0085A1",
        "color-link": "#008AFF",
        "color-link-hover": "#0085A1",
    },
}

html_title = "CLAMS Project"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Don't include .rst sources in build
html_copy_source = False

# -- Extension configuration -------------------------------------------------

# Intersphinx mapping - links to other documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'mmif-python': ('https://clams.ai/mmif-python/latest/', None),
    'clams-python': ('https://clams.ai/clams-python/latest/', None),
}

# Napoleon settings (for docstring parsing)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
}

# MyST parser settings (Markdown support)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
]
