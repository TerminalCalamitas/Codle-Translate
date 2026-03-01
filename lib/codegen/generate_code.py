def generate_code(output_language_skeleton: dict, program_ast) -> str:
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
            sub_code = generate_code(output_language_skeleton, value)
            code = code.replace(f"%{key}%", sub_code)

        elif isinstance(value, list):
            sub_parts = []
            for item in value:
                if isinstance(item, dict) and "element" in item:
                    sub_parts.append(generate_code(output_language_skeleton, item))
                else:
                    sub_parts.append(str(item))
            code = code.replace(f"%{key}%", "\n".join(sub_parts))

        else:
            code = code.replace(f"%{key}%", str(value))

    return code
