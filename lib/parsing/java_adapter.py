def java_to_ast(root, source: str):
    ast = []

    for node in root.children:
        element = _parse_node(node, source)
        if element:
            if isinstance(element, list):
                ast.extend(element)
            else:
                ast.append(element)

    return ast


def _parse_node(node, source):
    t = node.type

    # -------------------
    # Comments
    # -------------------
    if t == "line_comment":
        text = source[node.start_byte : node.end_byte]
        text = text.replace("//", "").strip()
        return {"element": "comment", "text": text}

    if t == "block_comment":
        text = source[node.start_byte : node.end_byte]
        text = text.replace("/*", "").replace("*/", "").strip()
        return {"element": "comment", "text": text}

    # -------------------
    # Variable Declaration
    # Example: int i = 0;
    # -------------------
    if t == "local_variable_declaration":
        text = source[node.start_byte : node.end_byte]
        text = text.rstrip(";").strip()

        # Very simple parsing (basic only)
        parts = text.split()
        type_ = parts[0]

        if "=" in text:
            left, value = text.split("=", 1)
            name = left.split()[-1].strip()
            return {
                "element": "assignment",
                "name": name,
                "type": type_,
                "value": value.strip(),
            }
        else:
            # Declaration without assignment
            name = parts[-1]
            return {"element": "assignment", "name": name, "type": type_, "value": None}

    # -------------------
    # Assignment
    # Example: i = 5;
    # -------------------
    if t == "expression_statement":
        text = source[node.start_byte : node.end_byte].strip()
        text = text.rstrip(";")

        if "System.out.println" in text:
            value = text[text.find("(") + 1 : text.rfind(")")]
            return {"element": "print", "value": value.strip()}

        if "=" in text and "==" not in text:
            name, value = text.split("=", 1)
            return {
                "element": "assignment",
                "name": name.strip(),
                "type": None,
                "value": value.strip(),
            }

    # -------------------
    # For loop
    # -------------------
    if t == "for_statement":
        init = node.child_by_field_name("initializer")
        condition = node.child_by_field_name("condition")
        update = node.child_by_field_name("update")
        body = node.child_by_field_name("body")

        return {
            "element": "for",
            "init": _node_text(init, source),
            "condition": _node_text(condition, source),
            "increment": _node_text(update, source),
            "body": _parse_block(body, source),
        }

    # -------------------
    # If statement
    # -------------------
    if t == "if_statement":
        condition = node.child_by_field_name("condition")
        consequence = node.child_by_field_name("consequence")

        return {
            "element": "if",
            "condition": _node_text(condition, source),
            "body": _parse_block(consequence, source),
        }

    # -------------------
    # While loop
    # -------------------
    if t == "while_statement":
        condition = node.child_by_field_name("condition")
        body = node.child_by_field_name("body")

        return {
            "element": "while",
            "condition": _node_text(condition, source),
            "body": _parse_block(body, source),
        }

    return None


def _parse_block(node, source):
    """
    Parse block statements recursively.
    """
    if node is None:
        return []

    elements = []

    for child in node.children:
        parsed = _parse_node(child, source)
        if parsed:
            if isinstance(parsed, list):
                elements.extend(parsed)
            else:
                elements.append(parsed)

    return elements


def _node_text(node, source):
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].strip()
