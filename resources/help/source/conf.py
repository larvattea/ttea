"""Sphinx configuration of the T-TEA user help.

The pages are written in Portuguese (pt_BR). English and Spanish come
from the catalogs in ``../locale``. Build with ``buildhelp.py``, which
sets the language, the help namespace and the title of each build.
"""

project = "Plataforma T-TEA"
author = "Udesc - Larva"
copyright = "2025-%Y, Udesc - Larva"

# -- Language and translations ------------------------------------------
language = "pt_BR"
locale_dirs = ["../locale/"]
# One catalog per page: smaller files, easier to translate and review.
gettext_compact = False
# Also translate the index keywords (Index tab of the help window).
gettext_additional_targets = ["index"]
# Language-specific images: foo.en_US.png replaces foo.png in the
# en_US build. Images without a variant are shared by all languages.
figure_language_filename = "{root}.{language}{ext}"

# -- Content ------------------------------------------------------------
exclude_patterns = ["_build"]
html_static_path = ["_static"]
html_css_files = ["ajuda.css"]
html_copy_source = False
html_show_sourcelink = False
html_title = "Ajuda da Plataforma T-TEA"

# -- Qt Help (.qhp/.qch) --------------------------------------------------
qthelp_basename = "ttea"
# Host part of the help URLs: lowercase and without "_". Set for each
# language by buildhelp.py.
qthelp_namespace = "br.udesc.larva.ttea.pt-br"
