"""Sphinx configuration for unihan-etl."""

from __future__ import annotations

import pathlib
import sys
import typing as t

if t.TYPE_CHECKING:
    from docutils import nodes
    from sphinx import addnodes
    from sphinx.application import Sphinx
    from sphinx.domains.python import PythonDomain
    from sphinx.environment import BuildEnvironment

from gp_sphinx.config import make_linkcode_resolve, merge_sphinx_config
from pygments import token
from pygments.lexer import RegexLexer, bygroups as _bygroups
from pygments.token import Keyword, Literal, Name, Operator, Punctuation
from sphinx.highlighting import lexers

import unihan_etl

bygroups: t.Callable[..., t.Any] = _bygroups

# Get the project root dir, which is the parent dir of this
cwd = pathlib.Path(__file__).parent
project_root = cwd.parent
src_root = project_root / "src"

sys.path.insert(0, str(src_root))

# package data
about: dict[str, str] = {}
with (src_root / "unihan_etl" / "__about__.py").open() as fp:
    exec(fp.read(), about)

conf = merge_sphinx_config(
    project=about["__title__"],
    version=about["__version__"],
    copyright=about["__copyright__"],
    source_repository=f"{about['__github__']}/",
    docs_url=about["__docs__"],
    source_branch="master",
    light_logo="img/cihai.svg",
    dark_logo="img/cihai.svg",
    extra_extensions=[
        "sphinx_argparse_neo.exemplar",
        "sphinx_autodoc_pytest_fixtures",
    ],
    intersphinx_mapping={
        "python": ("https://docs.python.org/3", None),
        "typing_extensions": (
            "https://typing-extensions.readthedocs.io/en/latest/",
            None,
        ),
        "mypy": ("https://mypy.readthedocs.io/en/stable/", None),
        "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
    },
    linkcode_resolve=make_linkcode_resolve(unihan_etl, about["__github__"]),
    html_favicon="_static/favicon.ico",
    html_extra_path=["manifest.json"],
    rediraffe_redirects="redirects.txt",
)
globals().update(conf)


class CsvLexer(RegexLexer):
    """Simple CSV lexer for Pygments.

    Credit: https://github.com/fish2000/pygments-csv-lexer/blob/8c18fbc/csvlexer/csv.py
    Original Author: SashaChernykh, Editor: fish2000
    License: MIT
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

    Based on CsvLexer, see credit above.
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


def _on_missing_class_reference(
    app: Sphinx,
    env: BuildEnvironment,
    node: addnodes.pending_xref,
    contnode: nodes.TextElement,
) -> nodes.reference | None:
    if node.get("refdomain") != "py" or node.get("reftype") != "class":
        return None
    from sphinx.util.nodes import make_refnode

    py_domain: PythonDomain = env.get_domain("py")  # type: ignore[assignment]
    target = node.get("reftarget", "")
    matches = py_domain.find_obj(env, "", "", target, None, 1)
    if not matches:
        return None
    _name, obj_entry = matches[0]
    return make_refnode(
        app.builder,
        node.get("refdoc", ""),
        obj_entry.docname,
        obj_entry.node_id,
        contnode,
    )


def setup(app: Sphinx) -> None:
    """Connect missing-reference handler to resolve py:data as :class: links."""
    app.connect("missing-reference", _on_missing_class_reference)
