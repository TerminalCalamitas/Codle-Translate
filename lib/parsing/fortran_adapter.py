def fortran_to_ast(root, source):
    ast = []

    for node in root.children:
        text = source[node.start_byte : node.end_byte].strip()

        if text.startswith("!"):
            ast.append({"element": "comment", "text": text[1:].strip()})

        elif "::" in text:
            print(text)
            type_, rest = text.split("::")
            name = rest.strip()
            ast.append(
                {
                    "element": "assignment",
                    "name": name,
                    "type": type_.strip(),
                    "value": None,
                }
            )

        elif text.startswith("print"):
            value = text.split(",", 1)[1].strip()
            ast.append({"element": "print", "value": value})

        elif text.startswith("do "):
            ast.append(
                {
                    "element": "for",
                    "init": "fortran_do",
                    "condition": "",
                    "increment": "",
                    "body": [],
                }
            )

        elif text.startswith("if"):
            ast.append({"element": "if", "condition": text, "body": []})

    return ast
