# flake8: NOQA: E501
"""Sphinx configuration for unihan-etl."""

from __future__ import annotations

import inspect
import pathlib
import sys
import typing as t
from os.path import relpath

from pygments import token
from pygments.lexer import RegexLexer, bygroups
from pygments.token import Keyword, Literal, Name, Operator, Punctuation
from sphinx.highlighting import lexers

import unihan_etl

if t.TYPE_CHECKING:
    from sphinx.application import Sphinx

# Get the project root dir, which is the parent dir of this
cwd = pathlib.Path(__file__).parent
project_root = cwd.parent
src_root = project_root / "src"

sys.path.insert(0, str(src_root))
sys.path.insert(0, str(cwd / "_ext"))

# package data
about: dict[str, str] = {}
with (src_root / "unihan_etl" / "__about__.py").open() as fp:
    exec(fp.read(), about)

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.linkcode",
    "argparse_exemplar",  # Custom sphinx-argparse replacement
    "sphinx_inline_tabs",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinxext.rediraffe",
    "myst_parser",
    "linkify_issues",
]
myst_enable_extensions = [
    "colon_fence",
    "substitution",
    "replacements",
    "strikethrough",
    "linkify",
]

templates_path = ["_templates"]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

master_doc = "index"

project = about["__title__"]
project_copyright = about["__copyright__"]

version = "{}".format(".".join(about["__version__"].split("."))[:2])
release = "{}".format(about["__version__"])

exclude_patterns = ["_build"]

pygments_style = "monokai"
pygments_dark_style = "monokai"

html_static_path = ["_static"]
html_extra_path = ["manifest.json"]
html_css_files = ["css/custom.css", "css/argparse-highlight.css"]
html_favicon = "_static/favicon.ico"
html_theme = "furo"
html_theme_path: list[str] = []
html_theme_options: dict[str, str | list[dict[str, str]]] = {
    "light_logo": "img/cihai.svg",
    "dark_logo": "img/cihai.svg",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": about["__github__"],
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": f"{about['__github__']}/",
    "source_branch": "master",
    "source_directory": "docs/",
}
html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/projects.html",
        "sidebar/scroll-end.html",
    ],
}

# linkify_issues
issue_url_tpl = about["__github__"] + "/issues/{issue_id}"

# sphinx.ext.autodoc
autoclass_content = "both"
autodoc_member_order = "bysource"
toc_object_entries_show_parents = "hide"
autodoc_default_options = {
    "undoc-members": True,
    "members": True,
    "private-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}

# sphinx-autodoc-typehints
autodoc_typehints = "description"  # show type hints in doc body instead of signature
simplify_optional_unions = True

# sphinx.ext.napoleon
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# sphinxext.opengraph
ogp_site_url = about["__docs__"]
ogp_image = "_static/img/icons/icon-192x192.png"
ogp_site_name = about["__title__"]

# sphinx-copybutton
copybutton_prompt_text = (
    r">>> |\.\.\. |> |\$ |\# | In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True

# sphinxext-rediraffe
rediraffe_redirects = "redirects.txt"
rediraffe_branch = "master~1"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "typing_extensions": ("https://typing-extensions.readthedocs.io/en/latest/", None),
    "mypy": ("https://mypy.readthedocs.io/en/stable/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
}


def linkcode_resolve(domain: str, info: dict[str, str]) -> None | str:
    """
    Determine the URL corresponding to Python object.

    Notes
    -----
    From https://github.com/numpy/numpy/blob/v1.15.1/doc/source/conf.py, 7c49cfa
    on Jul 31. License BSD-3. https://github.com/numpy/numpy/blob/v1.15.1/LICENSE.txt
    """
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except Exception:  # noqa: PERF203
            return None

    # strip decorators, which would resolve to the source of the decorator
    # possibly an upstream bug in getsourcefile, bpo-1764286
    try:
        unwrap = inspect.unwrap
    except AttributeError:
        pass
    else:
        if callable(obj):
            obj = unwrap(obj)

    try:
        fn = inspect.getsourcefile(obj)
    except Exception:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:
        lineno = None

    linespec = f"#L{lineno}-L{lineno + len(source) - 1}" if lineno else ""

    fn = relpath(fn, start=pathlib.Path(unihan_etl.__file__).parent)

    if "dev" in about["__version__"]:
        return "{}/blob/master/{}/{}/{}{}".format(
            about["__github__"],
            "src",
            about["__package_name__"],
            fn,
            linespec,
        )
    return "{}/blob/v{}/{}/{}/{}{}".format(
        about["__github__"],
        about["__version__"],
        "src",
        about["__package_name__"],
        fn,
        linespec,
    )


class CsvLexer(RegexLexer):
    """Simple CSV lexer for Pygments.

    Credit: https://github.com/fish2000/pygments-csv-lexer/blob/8c18fbc/csvlexer/csv.py
    Original Author: SashaChernykh, Editor: fish2000
    License: MIT

    Extends:
        pygments.lexer.RegexLexer

    Class Variables:
        name {str} -- name of lexer:
            * http://pygments.org/docs/api/#pygments.lexer.Lexer.name
        aliases {list} - languages, against whose GFM block names CsvLexer will apply
            * https://git.io/fhjla
        filenames {list} - file name patterns, for whose contents CsvLexer will apply
        tokens {dict} - regular expressions internally matching CsvLexer's components

    Based on StackOverflow user Adobe's code:
        * https://stackoverflow.com/a/25508711/298171
    """

    name = "Csv"
    aliases: t.ClassVar = [
        "csv",
        "comma-separated",
        "comma-separated-values",
    ]
    filenames: t.ClassVar[list[str]] = ["*.csv"]

    csv_pattern: str = r"(,)((\".*\")|[^,\n]*)"

    tokens: t.ClassVar = {
        "root": [
            (r"^[^,\n]*", Operator, "second"),
        ],
        "second": [
            (csv_pattern, bygroups(Punctuation, Name.Constant), "third"),
        ],
        "third": [
            (csv_pattern, bygroups(Punctuation, Keyword.Declaration), "fourth"),
        ],
        "fourth": [
            (csv_pattern, bygroups(Punctuation, Literal.Number), "fifth"),
        ],
        "fifth": [
            (csv_pattern, bygroups(Punctuation, Literal.String.Single), "sixth"),
        ],
        "sixth": [
            (csv_pattern, bygroups(Punctuation, Name.Constant), "seventh"),
        ],
        "seventh": [
            (csv_pattern, bygroups(Punctuation, Keyword.Namespace), "eighth"),
        ],
        "eighth": [
            (csv_pattern, bygroups(Punctuation, Literal.Number), "ninth"),
        ],
        "ninth": [
            (csv_pattern, bygroups(Punctuation, Literal.String.Single), "tenth"),
        ],
        "tenth": [
            (csv_pattern, bygroups(Punctuation, Keyword.Type), "unsupported"),
        ],
        "unsupported": [
            (r"(.+)", bygroups(Punctuation)),
        ],
    }


lexers["csv"] = CsvLexer()


class TsvLexer(CsvLexer):
    """Simple TSV lexer for Pygments.

    Based on CsvLexer, see credit above

    Extends:
        pygments.lexer.RegexLexer

    Class Variables:
        name {str} -- name of lexer:
            * http://pygments.org/docs/api/#pygments.lexer.Lexer.name
        aliases {list} - languages, against whose GFM block names CsvLexer will apply
            * https://git.io/fhjla
        filenames {list} - file name patterns, for whose contents CsvLexer will apply
        tokens {dict} - regular expressions internally matching CsvLexer's components

    Based on StackOverflow user Adobe's code:
        * https://stackoverflow.com/a/25508711/298171
    """

    tsv_pattern = r"([ \t]+)([^[\t\n]*)"

    name = "Tsv"
    aliases: t.ClassVar[list[str]] = ["tsv", "tab-separated", "tab-separated-values"]
    filenames: t.ClassVar[list[str]] = ["*.tsv"]

    tokens: t.ClassVar = {
        "root": [
            (r"^[^\t\n]*", token.Name.Constant, "second"),
        ],
        "second": [
            (
                tsv_pattern,
                bygroups(Punctuation, Name.Attribute),
                "third",
            ),
        ],
        "third": [
            (
                tsv_pattern,
                bygroups(Punctuation, token.Text),
                "fourth",
            ),
        ],
        "fourth": [
            (tsv_pattern, bygroups(Punctuation, Literal.Number), "fifth"),
        ],
        "fifth": [
            (tsv_pattern, bygroups(Punctuation, Literal.String.Single), "sixth"),
        ],
        "sixth": [
            (tsv_pattern, bygroups(Punctuation, Name.Constant), "seventh"),
        ],
        "seventh": [
            (tsv_pattern, bygroups(Punctuation, Keyword.Namespace), "eighth"),
        ],
        "eighth": [
            (tsv_pattern, bygroups(Punctuation, Literal.Number), "ninth"),
        ],
        "ninth": [
            (tsv_pattern, bygroups(Punctuation, Literal.String.Single), "tenth"),
        ],
        "tenth": [
            (tsv_pattern, bygroups(Punctuation, Keyword.Type), "unsupported"),
        ],
        "unsupported": [
            (r"(.+)", bygroups(Punctuation)),
        ],
    }


lexers["tsv"] = TsvLexer()


def remove_tabs_js(app: Sphinx, exc: Exception) -> None:
    """Remove tabs.js from _static after build."""
    # Fix for sphinx-inline-tabs#18
    if app.builder.format == "html" and not exc:
        tabs_js = pathlib.Path(app.builder.outdir) / "_static" / "tabs.js"
        tabs_js.unlink(missing_ok=True)


def setup(app: Sphinx) -> None:
    """Configure Sphinx app hooks."""
