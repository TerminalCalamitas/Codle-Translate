from lib.parsing.tree_sitter_loader import load_language
from lib.parsing.python_adapter import python_to_ast
from lib.parsing.javascript_adapter import js_to_ast
from lib.parsing.c_adapter import c_to_ast
from lib.parsing.fortran_adapter import fortran_to_ast
from lib.parsing.java_adapter import java_to_ast


def parse_to_ast(language: str, code: str):
    parser = load_language(language)
    tree = parser.parse(code.encode("utf8"))
    root = tree.root_node

    match language.lower():
        case "python":
            return python_to_ast(root, code)
        case "javascript":
            return js_to_ast(root, code)
        case "c":
            return c_to_ast(root, code)
        case "fortran":
            return fortran_to_ast(root, code)
        case "java":
            return java_to_ast(root, code)
        case _:
            raise ValueError(f"Unsupported language: {language}")
