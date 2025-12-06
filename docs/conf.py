#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from importlib import metadata

# Make src importable
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------

project = "Pypubsub"
copyright = "Oliver Schoenborn"

try:
    release = metadata.version("Pypubsub")
except metadata.PackageNotFoundError:
    try:
        import pubsub

        release = getattr(pubsub, "__version__", "0.0.0")
    except Exception:
        release = "0.0.0"

version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "changelog.rst", "apidocs"]
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = f"{project} v{release} Documentation"
html_short_title = f"{project} v{release}"
html_static_path = ["_static"]
html_last_updated_fmt = "%b %d, %Y"
