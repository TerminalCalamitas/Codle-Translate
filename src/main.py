import re
import yaml
from collections import defaultdict

# ========= DEFAULT PLACEHOLDER PATTERNS =========
DEFAULT_PLACEHOLDER_PATTERNS = {
    "var_name": r"[A-Za-z_]\w*",
    "start": r"\d+",
    "end": r"\d+",
    "var_value": r"[^;]+",  # up to the next semicolon
    "condition": r"[^)]+",  # inside parentheses
    "code": r"[\s\S]*?",  # any text (non-greedy)
}


# ========= LOAD SKELETON =========
def load_skeleton(lang: str) -> dict:
    """
    Load a skeleton YAML file from ./src/skeletons/{lang}.skeleton
    """
    with open(f"./src/skeletons/{lang}.skeleton") as skel:
        return yaml.safe_load(skel)


# ========= CONVERT SKELETON -> REGEX =========
def skeleton_to_regex(
    skel_str: str, placeholder_patterns: dict | None = None, use_backrefs: bool = False
):
    """
    Convert a skeleton string into a regex pattern.
    - use_backrefs=True : enforce repeated placeholders to be identical via backreferences.
    - use_backrefs=False: allow multiple occurrences with unique group names (post-process collapse).
    Returns: (compiled_regex, counts_dict)
    """
    placeholder_patterns = {
        **DEFAULT_PLACEHOLDER_PATTERNS,
        **(placeholder_patterns or {}),
    }
    parts = re.split(r"(%\w+%)", skel_str)  # keep placeholders in the split
    counts = defaultdict(int)
    regex_parts = []

    for token in parts:
        m = re.fullmatch(r"%(\w+)%", token)
        if m:
            name = m.group(1)
            counts[name] += 1
            pat = placeholder_patterns.get(name, r".+?")
            if use_backrefs:
                if counts[name] == 1:
                    regex_parts.append(f"(?P<{name}>{pat})")
                else:
                    regex_parts.append(f"(?P={name})")  # must match same as first
            else:
                grp = f"{name}__{counts[name]}"
                regex_parts.append(f"(?P<{grp}>{pat})")
        else:
            regex_parts.append(re.escape(token))

    full_pattern = r"^\s*" + "".join(regex_parts) + r"\s*$"
    compiled = re.compile(full_pattern, re.DOTALL)
    return compiled, dict(counts)


# ========= BUILD ALL PATTERNS =========
def build_patterns_from_skeletons(
    skeletons: dict,
    placeholder_patterns: dict | None = None,
    use_backrefs: bool = False,
):
    """
    Build regex patterns for all skeletons.
    Returns: patterns {element: regex}, metas {element: counts}.
    """
    patterns = {}
    metas = {}
    for element, skel in skeletons.items():
        compiled, counts = skeleton_to_regex(skel, placeholder_patterns, use_backrefs)
        patterns[element] = compiled
        metas[element] = counts
    return patterns, metas


# ========= PARSE CODE =========
def parse_code_with_patterns(
    code: str,
    patterns: dict,
    metas: dict,
    use_backrefs: bool = False,
    enforce_same: bool = False,
) -> dict | None:
    """
    Try to parse code using the compiled patterns.
    - If use_backrefs=True: repeated placeholders enforced equal at regex time.
    - If use_backrefs=False: repeated placeholders collapsed into single value if equal,
      or list of values if different (unless enforce_same=True -> error).
    """
    code = code.strip()
    for element, pattern in patterns.items():
        m = pattern.match(code)
        if not m:
            continue
        result = {"element": element}
        counts = metas[element]

        if use_backrefs:
            result.update({k: v for k, v in m.groupdict().items() if v is not None})
            return result

        # Collapse repeated groups
        for base, cnt in counts.items():
            values = [m.group(f"{base}__{i}") for i in range(1, cnt + 1)]
            values = [v.strip() if isinstance(v, str) else v for v in values]
            if all(v == values[0] for v in values):
                result[base] = values[0]
            else:
                if enforce_same:
                    raise ValueError(
                        f"Repeated placeholders for '{base}' differ: {values}"
                    )
                result[base] = values
        return result

    return None


def generate_code(skeleton, dict):
    element = dict["element"]
    template = skeleton[element]
    code = template

    for key, value in dict.items():
        if key == "element":
            continue
        code = code.replace(f"%{key}%", str(value))
    return code


# ========= EXAMPLE USAGE =========
if __name__ == "__main__":
    # Example skeletons (you can replace with load_skeleton("javascript"))
    """
    skeletons = {
        "variable": "let %var_name% = %var_value%;",
        "if": "if (%condition%) {\n    %code%\n}",
        "for": "for (let %var_name% = %start%; %var_name% < %end%; %var_name%++) {\n    %code%\n}",
    }
        """
    skeletons = load_skeleton("javascript")

    with open("./if.js") as if_data:
        if_code = if_data.read()

    with open("./for.js") as for_data:
        for_code = for_data.read()

    # Build patterns
    patterns, metas = build_patterns_from_skeletons(skeletons, use_backrefs=True)
    for_loop_in_js = parse_code_with_patterns(
        for_code,
        patterns,
        metas,
        use_backrefs=True,
    )

    # Test
    print(parse_code_with_patterns("let x = 42;", patterns, metas, use_backrefs=True))
    print(parse_code_with_patterns(if_code, patterns, metas, use_backrefs=True))
    print(for_loop_in_js)

    py_skel = load_skeleton("python")
    print(generate_code(py_skel, for_loop_in_js))

    py_skel = load_skeleton("python")
    py_patterns, py_metas = build_patterns_from_skeletons(py_skel, use_backrefs=True)
    print(py_patterns)

    with open("./code.py") as for_data:
        py_for_code = for_data.read()

    # Parse Python code into dict
    for_loop_in_py = parse_code_with_patterns(
        py_for_code,
        py_patterns,
        py_metas,
        use_backrefs=True,
    )

    # Generate JavaScript from dict
    jva_skel = load_skeleton("fortran")
    print(generate_code(jva_skel, for_loop_in_js))
