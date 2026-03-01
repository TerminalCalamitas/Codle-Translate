def parse_program(code: str, patterns: dict, placeholder_count: dict, **kwargs):
    """
    Parse a full code file consisting of multiple statements.
    Returns a list of parsed statement dicts.
    """
    results = []
    remaining = code

    while remaining:
        remaining = remaining.lstrip("\n")  # remove leading newlines only
        if not remaining.strip():
            break

        matched = False

        for element, pattern in patterns.items():
            m = pattern.match(remaining)
            if not m:
                continue

            matched = True
            snippet = m.group(0)
            parsed = parse_code_with_patterns(
                snippet, patterns, placeholder_count, **kwargs
            )

            # If the snippet has a 'code' placeholder that contains multiple statements, parse recursively
            if parsed and "code" in parsed and isinstance(parsed["code"], str):
                nested_statements = parse_program(
                    parsed["code"], patterns, placeholder_count, **kwargs
                )
                if nested_statements:
                    parsed["code"] = nested_statements

            results.append(parsed)
            remaining = remaining[len(snippet) :]

        if not matched:
            # Could not match any pattern, skip one line
            next_line = remaining.split("\n", 1)
            remaining = next_line[1] if len(next_line) > 1 else ""

    return results


def parse_code_with_patterns(
    code: str,
    patterns: dict,
    placeholder_count: dict,
    use_backrefs: bool = False,
    enforce_same: bool = False,
) -> dict | None:
    """
    Try to parse code using the compiled patterns.
    Recursively parses any 'code' placeholders found.
    """
    code = code.strip()
    for element, pattern in patterns.items():
        m = pattern.match(code)
        if not m:
            continue
        result = {"element": element}
        counts = placeholder_count[element]

        if use_backrefs:
            result.update({k: v for k, v in m.groupdict().items() if v is not None})
        else:
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

        # === Recursive parsing for 'code' placeholder(s) ===
        if "code" in result and isinstance(result["code"], str):
            nested = parse_code_with_patterns(
                result["code"], patterns, placeholder_count, use_backrefs, enforce_same
            )
            if nested:
                result["code"] = nested

        # Handle multiple 'code' blocks (e.g. if an element has multiple)
        if isinstance(result.get("code"), list):
            result["code"] = [
                parse_code_with_patterns(
                    c, patterns, placeholder_count, use_backrefs, enforce_same
                )
                if isinstance(c, str)
                else c
                for c in result["code"]
            ]

        return result

    return None
