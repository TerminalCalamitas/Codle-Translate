from lib.skeleton_helper import load_skeleton
from lib.codegen import generate_code
from lib.parsing.parse_to_ast import parse_to_ast


def translate(fromLanguage: str, toLanguage: str, code: str) -> str:
    # Parse code into AST
    ast = parse_to_ast(fromLanguage, code)

    # Load Target Language Skeleton
    output_skeleton = load_skeleton(toLanguage)

    # Generate output code
    output_code = generate_code(output_skeleton, ast)

    return output_code
