def python_to_ast(root, source):
    ast = []

    for node in root.children:
        type = node.type

        if type == "comment":
            text = source[node.start_byte : node.end_byte].lstrip("# ").strip()
            ast.append({"element": "comment", "text": text})

        elif type == "expression_statement":
            text = source[node.start_byte : node.end_byte].strip()
            if text.startswith("print"):
                value = text[text.find("(") + 1 : text.rfind(")")]
                ast.append({"element": "print", "value": value})
            elif "=" in text:
                name, value = text.split("=", 1)
                ast.append(
                    {
                        "element": "assignment",
                        "name": name.strip(),
                        "type": None,
                        "value": value.strip(),
                    }
                )

        elif type == "for_statement":
            text = source[node.start_byte : node.end_byte]
            ast.append(
                {
                    "element": "for",
                    "init": "range_loop",
                    "condition": "python_range",
                    "increment": "",
                    "body": [],
                }
            )

        elif type == "if_statement":
            condition = source[
                node.child_by_field_name(
                    "condition"
                ).start_byte : node.child_by_field_name("condition").end_byte
            ]
            ast.append({"element": "if", "condition": condition, "body": []})

        elif type == "while_statement":
            condition = source[
                node.child_by_field_name(
                    "condition"
                ).start_byte : node.child_by_field_name("condition").end_byte
            ]
            ast.append({"element": "while", "condition": condition, "body": []})

    return ast
