import re


def _sub_ignore_strings(pattern: str, repl: str, text: str, flags: int = 0) -> str:
    """
    Making sure to only substitute outside of strings
    """
    _STRING_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
    result = []
    last = 0

    for match in _STRING_TOKEN.finditer(text):
        # Figure out stuff before the string
        gap = text[last : match.start()]
        result.append(re.sub(pattern, repl, gap, flags=flags))

        # Copy string to output
        result.append(match.group())
        last = match.end()
    #
    # Figure out text after strings
    result.append(re.sub(pattern, repl, text[last:], flags=flags))

    return "".join(result)


def normalize(expr: str) -> str:
    """
    Convert supported language's expression into neutral formatting
    """
    expression = expr.strip()

    expression = _sub_ignore_strings(r"!==|!=", "!=", expression)
    expression = _sub_ignore_strings(
        r"===|==", "==", expression
    )  # Fix for JavaScript since it is different
    expression = _sub_ignore_strings(r"\btrue\b", "True", expression)
    expression = _sub_ignore_strings(r"\bfalse\b", "False", expression)
    expression = _sub_ignore_strings(r"\bnull\b", "None", expression)
    expression = _sub_ignore_strings(r"\bNULL\b", "None", expression)
    expression = _sub_ignore_strings(r"&&", " and ", expression)
    expression = _sub_ignore_strings(r"\|\|", " or ", expression)
    expression = _sub_ignore_strings(
        r"!(?!=)", " not ", expression
    )  # Change ! separate from != to 'not'

    return expression.strip()


def denormalize(expr: str, lang: str) -> str:
    """
    Convert neutral formatted expression into the target language
    """
    if lang == "python":  # Code is already formatted for python
        return expr

    expression = expr
    expression = _sub_ignore_strings(r"\bTrue\b", "true", expression)
    expression = _sub_ignore_strings(r"\bFalse\b", "false", expression)
    expression = _sub_ignore_strings(
        r"\bNone\b", "NULL" if lang == "c" else "null", expression
    )
    expression = _sub_ignore_strings(r"\band\b", "&&", expression)
    expression = _sub_ignore_strings(r"\bor\b", "||", expression)
    expression = _sub_ignore_strings(r"\bnot\b\s*", "!", expression)

    return expression


def infer_type(value: str) -> str:
    """
    Determine variable type based on value
    """

    value = value.strip()
    if value in ("True", "False", "true", "false"):
        return "bool"

    if re.fullmatch(r"-?\d+", value):
        return "int"

    if re.fullmatch(r"-?\d+\.\d*f?", value):
        return "float"

    if re.fullmatch(r'["\'].*["\']', value, re.DOTALL):
        return "str"

    return "unknown"
