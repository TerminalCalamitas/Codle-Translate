def c_to_ast(root, source):
    ast = []

    for node in root.children:
        t = node.type

        if t == "comment":
            text = source[node.start_byte : node.end_byte]
            ast.append({"element": "comment", "text": text.strip("/* ").strip()})

        elif t == "declaration":
            text = source[node.start_byte : node.end_byte]
            text = text.replace(";", "")
            parts = text.split()
            type_ = parts[0]
            name = parts[1]
            value = parts[3]
            ast.append(
                {
                    "element": "assignment",
                    "name": name.strip(),
                    "type": type_,
                    "value": value.strip(),
                }
            )

        elif t == "expression_statement":
            text = source[node.start_byte : node.end_byte]
            if "printf" in text:
                value = text[text.find("(") + 1 : text.rfind(")")]
                ast.append({"element": "print", "value": value})

        elif t == "for_statement":
            ast.append(
                {
                    "element": "for",
                    "init": "c_for",
                    "condition": "c_condition",
                    "increment": "c_increment",
                    "body": [],
                }
            )

    return ast
