from tree_sitter_language_pack import get_language, get_parser, get_binding

LANGUAGES = {}
BINDINGS = {}


def load_language(language: str):
    if not LANGUAGES:
        LANGUAGES["python"] = get_language("python")
        LANGUAGES["javascript"] = get_language("javascript")
        LANGUAGES["c"] = get_language("c")
        LANGUAGES["fortran"] = get_language("fortran")
        LANGUAGES["java"] = get_language("java")

    if not BINDINGS:
        BINDINGS["python"] = get_binding("python")
        BINDINGS["javascript"] = get_binding("javascript")
        BINDINGS["c"] = get_binding("c")
        BINDINGS["fortran"] = get_binding("fortran")
        BINDINGS["java"] = get_binding("java")

    parser = get_parser(language.lower())
    return parser
