def ast_fix(ast, toLanguage: str, fromLanguage: str):
    # if passed a list, recall as a dictionary
    if isinstance(ast, list):
        return [ast_fix(item, toLanguage, fromLanguage) for item in ast]

    for key, value in ast.items():
        if key == "element":
            continue

        if key == "assignment":
            if value.lower() == "true" or value.lower() == "false":
                if toLanguage == "python":
                    value = value.capitalize()
                elif fromLanguage == "python":
                    value = value.lower()
        if toLanguage == "javascript":
            value.replaceall("==", "===")
        elif fromLanguage == "javascript":
            value.replaceall("===", "==")

    return ast
