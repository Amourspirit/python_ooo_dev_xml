# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

_DOCS_PATH = Path(__file__).parent
_ROOT_PATH = _DOCS_PATH.parent

sys.path.insert(0, str(_ROOT_PATH))


os.environ["DOCS_BUILDING"] = "True"
os.environ["ooouno_ignore_runtime"] = "True"


def get_spell_dictionaries() -> list:
    p = _DOCS_PATH.absolute().resolve() / "internal" / "dict"
    dict_gen = p.glob("spelling_*.*")
    return [str(d) for d in dict_gen if d.is_file()]


# -- Project information -----------------------------------------------------

project = "ooo-dev-xml"
copyright = "2023, :Barry-Thomas-Paul: Moss"
author = ":Barry-Thomas-Paul: Moss"
release = "0.1.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinx_rtd_dark_mode",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_toolbox.collapse",
    "sphinx_toolbox.more_autodoc.autonamedtuple",
    "sphinx_toolbox.more_autodoc.typevars",
    "sphinx_toolbox.more_autodoc.autoprotocol",
    "sphinx_toolbox.more_autodoc.overloads",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_tabs.tabs",
    "sphinx_design",
    "sphinxcontrib.spelling",
    "sphinx-prompt",
    "sphinx_substitution_extensions",
    "sphinx_copybutton",
]

# "sphinx.ext.linkcode",
# sphinx_tabs.tabs docs: https://sphinx-tabs.readthedocs.io/en/latest/

# "sphinx_design"
# https://sphinx-design.readthedocs.io/en/rtd-theme/get_started.html

# region spelling
# https://sphinxcontrib-spelling.readthedocs.io/en/latest/

# sphinx_substitution_extensions
# https://github.com/adamtheturtle/sphinx-substitution-extensions

# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-suppress_warnings
# https://github.com/sphinx-doc/sphinx/issues/4961
# List of zero or more Sphinx-specific warning categories to be squelched (i.e.,
# suppressed, ignored).
suppress_warnings = [
    # FIXME: *THIS IS TERRIBLE.* Generally speaking, we do want Sphinx to inform
    # us about cross-referencing failures. Remove this hack entirely after Sphinx
    # resolves this open issue:
    #    https://github.com/sphinx-doc/sphinx/issues/4961
    # Squelch mostly ignorable warnings resembling:
    #     WARNING: more than one target found for cross-reference 'TypeHint':
    #     beartype.door._doorcls.TypeHint, beartype.door.TypeHint
    "ref.python",
]

spelling_word_list_filename = get_spell_dictionaries()

spelling_show_suggestions = True
spelling_ignore_pypi_package_names = True
spelling_ignore_contributor_names = True
spelling_ignore_acronyms = True

# https://sphinxcontrib-spelling.readthedocs.io/en/latest/customize.html
spelling_exclude_patterns = [".venv/"]

# spell checking;
#   run sphinx-build -b spelling . _build
#       this will check for any spelling and create folders with *.spelling files if there are errors.
#       open each *.spelling file and find any spelling errors and fix them in corresponding files.
#
# spelling_book.txt contains all spelling exceptions related to book in /docs/odev
# spelling_code.txt contains all spelling exceptions related to python doc strings.

# endregion spelling


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"]
if html_theme == "sphinx_rtd_theme":
    html_css_files.append("css/readthedocs_custom.css")

if "sphinx_rtd_dark_mode" in extensions:
    html_css_files.append("css/readthedocs_dark.css")

html_css_files.append("css/style_custom.css")

html_js_files = [
    "js/custom.js",
]

# Napoleon settings
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# https://fossies.org/linux/Sphinx/doc/usage/extensions/autodoc.rst
# This value controls how to represent type hints. The setting takes the following values:
autodoc_typehints = "description"

# https://documentation.help/Sphinx/autodoc.html
autoclass_content = "init"


# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_mock_imports
# see: https://read-the-docs.readthedocs.io/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
# on read the docs I was getting errors WARNING: autodoc: failed to import class - No module named 'uno'
# solution autodoc_mock_imports, for some reason after adding uno, unohelper I also had to include com.
# com.sun.star.__init__.py raises an Import error by design.
autodoc_mock_imports = ["uno", "unohelper", "lxml", "com"]

# set is todo's will show up.
# a master list of todo's will be on bottom of main page.
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#module-sphinx.ext.todo
todo_include_todos = False

# region copybutton
# https://pypi.org/project/sphinx-copybutton/
# copybutton_exclude = '.linenos, .gp, .go'
copybutton_prompt_text = r">>> ?|\.\.\. ?|\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
# endregion copybutton
