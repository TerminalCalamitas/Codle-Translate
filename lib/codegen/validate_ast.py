from lib.codegen.placeholders import PLACEHOLDERS


def validate_node(node: dict):
    if "element" not in node:
        raise ValueError("AST node missing 'element'")

    element = node["element"]

    if element not in PLACEHOLDERS:
        raise ValueError(f"Unknown AST element: {element}")

    allowed = PLACEHOLDERS[element] | {"element"}

    extra = set(node.keys()) - allowed
    if extra:
        raise ValueError(f"Unexpected fields in {element}: {extra}")

    # Body validation
    if "body" in node:
        if not isinstance(node["body"], list):
            raise ValueError(f"'body' in {element} must be list")

        for child in node["body"]:
            validate_node(child)


def validate_program(ast):
    if not isinstance(ast, list):
        raise ValueError("Program AST must be list")
    for node in ast:
        validate_node(node)
