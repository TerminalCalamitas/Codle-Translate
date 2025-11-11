from collections import defaultdict
import os
import re
import yaml


def load_skeleton(lang: str) -> dict:
    """
    Load a skeleton YAML file from ./src/skeletons/{lang}.skeleton
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    skeletons_dir = os.path.join(current_dir, "../skeletons")
    skeleton_file_path = os.path.join(skeletons_dir, f"{lang}.skeleton")

    with open(skeleton_file_path) as skel:
        return yaml.safe_load(skel)


def skeleton_to_regex(
    skel_str: str, placeholder_patterns: dict | None = None, use_backrefs: bool = False
):
    """
    Convert a skeleton string into a regex pattern.

    use_backrefs=True : Multiple of the same placeholders will be counted as the same variable.
    use_backrefs=False: Allows multiple of the same placeholders to count for different variables.

    Returns: (compiled_regex, counts_dict)
    """

    DEFAULT_PLACEHOLDER_PATTERNS = {
        "var_name": r"[A-Za-z_]\w*",  # Single word that starts with letter or _
        "start": r"\d+",  # some number
        "end": r"\d+",  # some number
        "var_value": r"[^;]+",  # up to the next semicolon
        "condition": r"[^)]+",  # inside parentheses
        "code": r"[\s\S]*?",  # any text (non-greedy)
        "string": r"[^\n]+",  # anything not a newline
    }

    placeholder_patterns = {
        **DEFAULT_PLACEHOLDER_PATTERNS,
        **(placeholder_patterns or {}),
    }

    parts = re.split(r"(%\w+%)", skel_str)  # keep placeholders in the split
    counts = defaultdict(int)
    regex_parts = []

    for token in parts:
        match = re.fullmatch(r"%(\w+)%", token)

        if match:
            name = match.group(1)
            counts[name] += 1
            pattern = placeholder_patterns.get(name, r".+?")

            if use_backrefs:
                if counts[name] == 1:
                    regex_parts.append(f"(?P<{name}>{pattern})")

                else:
                    regex_parts.append(f"(?P={name})")  # must match same as first

            else:
                group = f"{name}__{counts[name]}"
                regex_parts.append(f"(?P<{group}>{pattern})")

        else:
            regex_parts.append(re.escape(token))

    full_pattern = r"^\s*" + "".join(regex_parts) + r"\s*$"
    compiled = re.compile(full_pattern, re.DOTALL)
    return compiled, dict(counts)


def build_patterns_from_skeletons(
    skeleton: dict,
    placeholder_patterns: dict | None = None,
    use_backrefs: bool = False,
):
    """
    Build regex patterns for all entries in skeleton.

    Returns: patterns {element: regex}, placeholder_count {element: count}.
    """
    patterns = {}
    placeholder_count = {}

    for element, skel in skeleton.items():
        compiled, counts = skeleton_to_regex(skel, placeholder_patterns, use_backrefs)

        patterns[element] = compiled
        placeholder_count[element] = counts

    return patterns, placeholder_count
