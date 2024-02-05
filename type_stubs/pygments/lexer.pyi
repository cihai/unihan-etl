import typing as t

if t.TYPE_CHECKING:
    from pygments.token import _TokenType

class Lexer:
    name: str | None = None
    aliases: t.ClassVar[list[str]]
    filenames: t.ClassVar[list[str]]
    alias_filenames: t.ClassVar[list[str]]
    mime_types: t.ClassVar[list[str]]
    priority: int
    ulr: str

    def __init__(self, options: dict[str, object] | None = None) -> None: ...

class RegexLexer(Lexer): ...

def bygroups(
    *args: Lexer | _TokenType,
) -> t.Generator[None, Lexer | _TokenType, None]: ...
