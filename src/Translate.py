from lib.skeleton_helper import load_skeleton, build_patterns_from_skeletons
from lib.parser import parse_program


def translate(fromLanguage: str, toLanguage: str, code: str) -> str:
    print("code: " + code)
    # load skeletons
    print("loading skeletons")
    input_skeleton = load_skeleton(fromLanguage)
    output_skeleton = load_skeleton(toLanguage)
    print("skeletons loaded")

    # build patterns and placeholder counts
    print("building patterns")
    input_patterns, input_placeholder_count = build_patterns_from_skeletons(
        input_skeleton, use_backrefs=True
    )
    output_patterns, output_placeholder_count = build_patterns_from_skeletons(
        output_skeleton, use_backrefs=True
    )
    print("patterns built")

    # make abstract syntax tree ast for program
    print("making ast")
    program_ast = parse_program(
        code, input_patterns, input_placeholder_count, use_backrefs=True
    )
    print("ast finished")

    # generate code
    print("generating code")
    translated_code = generate_code(output_skeleton, program_ast)

    print("code finished generating")
    print(translated_code)

    # return code
    return translated_code


def generate_code(output_language_skeleton: dict, program_ast):
    # if passed a list, recall as a dictionary
    if isinstance(program_ast, list):
        return "\n".join(
            generate_code(output_language_skeleton, d) for d in program_ast
        )

    element = program_ast.get("element")
    if element not in output_language_skeleton:
        raise ValueError(f"No skeleton for element '{element}'")

    template = output_language_skeleton[element]
    code = template

    for key, value in program_ast.items():
        if key == "element":
            continue

        # If it's a code segment then recall on the value
        if isinstance(value, dict) and "element" in value:
            sub_code = generate_code(skeletons, value)
            code = code.replace(f"%{key}%", sub_code)

        elif isinstance(value, list):
            sub_parts = []
            for item in value:
                if isinstance(item, dict) and "element" in item:
                    sub_parts.append(generate_code(skeletons, item))
                else:
                    sub_parts.append(str(item))
            code = code.replace(f"%{key}%", "\n".join(sub_parts))

        else:
            code = code.replace(f"%{key}%", str(value))

    return code
