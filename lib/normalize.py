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
    # Figure out text after strings
    result.append(re.sub(pattern, repl, text[last:], flags=flags))
    return "".join(result)


def normalize(expr: str) -> str:
    """
    Convert supported language's expression into neutral formatting
    """
    e = expr.strip()

    e = _sub_ignore_strings(r"!==|!=", "!=", e)
    e = _sub_ignore_strings(
        r"===|==", "==", e
    )  # Fix for JavaScript since it is different
    e = _sub_ignore_strings(r"\btrue\b", "True", e)
    e = _sub_ignore_strings(r"\bfalse\b", "False", e)
    e = _sub_ignore_strings(r"\bnull\b", "None", e)
    e = _sub_ignore_strings(r"\bNULL\b", "None", e)
    e = _sub_ignore_strings(r"&&", " and ", e)
    e = _sub_ignore_strings(r"\|\|", " or ", e)
    e = _sub_ignore_strings(r"!(?!=)", " not ", e)  # Change ! separate from != to 'not'

    return e.strip()


def denormalize(expr: str, lang: str) -> str:
    """
    Convert neutral formatted expression into the target language
    """
    if lang == "python":  # Code is already formatted for python
        return expr

    e = expr
    e = _sub_ignore_strings(r"\bTrue\b", "true", e)
    e = _sub_ignore_strings(r"\bFalse\b", "false", e)
    e = _sub_ignore_strings(r"\bNone\b", "NULL" if lang == "c" else "null", e)
    e = _sub_ignore_strings(r"\band\b", "&&", e)
    e = _sub_ignore_strings(r"\bor\b", "||", e)
    e = _sub_ignore_strings(r"\bnot\b\s*", "!", e)

    return e


def infer_type(value: str) -> str:
    """
    Determine variable type based on value
    """

    v = value.strip()
    if v in ("True", "False", "true", "false"):
        return "bool"

    if re.fullmatch(r"-?\d+", v):
        return "int"

    if re.fullmatch(r"-?\d+\.\d*f?", v):
        return "float"

    if re.fullmatch(r'["\'].*["\']', v, re.DOTALL):
        return "str"

    return "unknown"
