def js_to_ast(root, source):
    ast = []

    for node in root.children:
        t = node.type

        if t == "comment":
            text = source[node.start_byte : node.end_byte]
            text = text.replace("//", "").strip()
            ast.append({"element": "comment", "text": text})

        elif t == "lexical_declaration":
            text = source[node.start_byte : node.end_byte]
            text = text.replace("let ", "").replace(";", "")
            name, value = text.split("=", 1)
            ast.append(
                {
                    "element": "assignment",
                    "name": name.strip(),
                    "type": None,
                    "value": value.strip(),
                }
            )

        elif t == "expression_statement":
            text = source[node.start_byte : node.end_byte]
            if "console.log" in text:
                value = text[text.find("(") + 1 : text.rfind(")")]
                ast.append({"element": "print", "value": value})

        elif t == "for_statement":
            header = source[node.start_byte : node.end_byte]
            ast.append(
                {
                    "element": "for",
                    "init": "js_for",
                    "condition": "js_condition",
                    "increment": "js_increment",
                    "body": [],
                }
            )

        elif t == "if_statement":
            condition = source[
                node.child_by_field_name(
                    "condition"
                ).start_byte : node.child_by_field_name("condition").end_byte
            ]
            ast.append({"element": "if", "condition": condition, "body": []})

        elif t == "while_statement":
            condition = source[
                node.child_by_field_name(
                    "condition"
                ).start_byte : node.child_by_field_name("condition").end_byte
            ]
            ast.append({"element": "while", "condition": condition, "body": []})

    return ast
