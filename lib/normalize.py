import re


def normalize(expr: str) -> str:
    """
    Convert supported language's expression into neutral formatting
    """
    e = expr.strip()

    e = re.sub(r"===|==", "==", e)  # Fix for JavaScript since it is different
    e = re.sub(r"!==|!=", "!=", e)
    e = re.sub(r"\btrue\b", "True", e)
    e = re.sub(r"\bfalse\b", "False", e)
    e = re.sub(r"\bnull\b", "None", e)
    e = re.sub(r"\bNULL\b", "None", e)
    e = re.sub(r"&&", " and ", e)
    e = re.sub(r"\|\|", " or ", e)
    e = re.sub(r"!(?!=)", " not ", e)  # Change ! separate from != to 'not'

    return e.strip()


def denormalize(expr: str, lang: str) -> str:
    """
    Convert neutral formatted expression into the target language
    """
    if lang == "python":  # Code is already formatted for python
        return expr

    e = expr
    e = re.sub(r"\bTrue\b", "true", e)
    e = re.sub(r"\bFalse\b", "false", e)
    e = re.sub(r"\bNone\b", "NULL" if lang == "c" else "null", e)
    e = re.sub(r"\band\b", "&&", e)
    e = re.sub(r"\bor\b", "||", e)
    e = re.sub(r"\bnot\s+", "!", e)

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
