import re
from typing import List
from lib.ir import (
    IRNode,
    IRVarAssign,
    IRPrint,
    IRForRange,
    IRWhileLoop,
    IRIfStatement,
    IRComment,
)
from lib.normalize import normalize, infer_type

try:
    from tree_sitter_language_pack import get_parser as _get_ts_parser

    _TS_AVAILABLE = True
except ImportError:
    _TS_AVAILABLE = False


def _node_text(node, src: bytes) -> str:
    return src[node.start_byte : node.end_byte].decode("utf-8")


# Tree Sitter Helpers


def _parse_block_body(block_node, src: bytes, lang_tag: str) -> List[IRNode]:
    """Recursively parse the children of a { } block into IR nodes."""
    results: List[IRNode] = []
    for child in block_node.children:
        nodes = _dispatch_node(child, src, lang_tag)
        results.extend(nodes)
    return results


def _dispatch_node(node, src: bytes, lang_tag: str) -> List[IRNode]:
    """
    Routes a single tree-sitter node to the appropriate IR builder.
    """
    node_type = node.type

    if node_type in ("comment", "line_comment", "block_comment"):
        raw = _node_text(node, src)
        # Strip //  or /* */  or  #
        text = re.sub(r"^//\s*", "", raw)
        text = re.sub(r"^/\*+\s*|\s*\*+/$", "", text)
        text = re.sub(r"^#\s*", "", text).strip()
        return [IRComment(text)]

    # Python Specific builders
    if node_type == "for_statement" and lang_tag == "python":
        return [_build_for_python(node, src)]

    if node_type == "assignment" and lang_tag == "python":
        return _build_var_python(node, src)

    # Generic builders
    if node_type == "for_statement":
        return [_build_for_c_style(node, src, lang_tag)]

    if node_type == "while_statement":
        return [_build_while(node, src, lang_tag)]

    if node_type == "if_statement":
        return [_build_if(node, src, lang_tag)]

    if node_type == "expression_statement":
        # Use first named child to skip punctuation tokens
        named = [child for child in node.children if child.is_named]
        inner = named[0] if named else (node.children[0] if node.children else node)
        return _dispatch_node(inner, src, lang_tag)

    # Convert varible++/-- to += or -=
    if node_type == "update_expression":
        raw = _node_text(node, src).strip()
        match = re.match(r"^(\w+)\s*(\+\+|--)$", raw) or re.match(
            r"^(\+\+|--)\s*(\w+)$", raw
        )
        if match:
            group = match.groups()
            var = group[0] if re.match(r"\w+", group[0]) else group[1]
            op = group[1] if re.match(r"\w+", group[0]) else group[0]
            delta = "1" if "++" in op else "-1"
            return [
                IRVarAssign(
                    var, f"{var} + {delta}" if delta == "1" else f"{var} - 1", "unknown"
                )
            ]
        return []

    if node_type == "call_expression":
        function = _node_text(
            node.child_by_field_name("function") or node.children[0], src
        )
        if function in (
            "console.log",
            "printf",
            "System.out.println",
            "System.out.print",
            "print",
            "cout",
        ):
            args_node = node.child_by_field_name("arguments")
            args_text = ""
            if args_node:
                raw_args = _node_text(args_node, src).strip("()")
                args_text = normalize(raw_args)
            return [IRPrint(args_text)]

    # Python Tree-Sitter uses 'call' instead of 'call_expression'
    if node_type == "call":
        function_node = node.child_by_field_name("function")
        function = _node_text(function_node, src).strip() if function_node else ""
        if function == "print":
            args_node = node.child_by_field_name("arguments")
            args_text = ""
            if args_node:
                raw_args = _node_text(args_node, src).strip("()")
                args_text = normalize(raw_args)
            return [IRPrint(args_text)]

    # Java uses 'method_invocation' for System.out.println and System.out.print
    if node_type == "method_invocation":
        raw = _node_text(node, src)
        if "System.out.print" in raw:
            args_node = node.child_by_field_name("arguments")
            args_text = ""
            if args_node:
                raw_args = _node_text(args_node, src).strip("()")
                args_text = normalize(raw_args)
            return [IRPrint(args_text)]

    # Variable declarations
    if node_type in ("lexical_declaration", "variable_declaration"):
        return _build_var_js(node, src)

    if node_type == "local_variable_declaration":  # Java
        return _build_var_java(node, src)

    if node_type == "declaration":  # C
        return _build_var_c(node, src)

    # Python specifications since it they are different than the other languages
    if node_type == "for_statement" and lang_tag == "python":
        return [_build_for_python(node, src)]

    if node_type == "assignment":
        return _build_var_python(node, src)

    if node_type == "expression_statement" and lang_tag == "python":
        pass

    return []


# Code builders


# Loop builders
def _parse_c_style_for(init_text: str, cond_text: str, incr_text: str):
    """
    Attempt to reduce a C-style for loop to a range triple (var, start, end, step).
    Returns (var, start, end, step) or None if the pattern isn't recognized.
    """
    # init:  (let|var|int|long|) i = 0
    match_init = re.match(
        r"(?:let|var|int|long|short|size_t|auto)?\s*(\w+)\s*=\s*(.+)",
        init_text.strip().rstrip(";"),
    )
    if not match_init:
        return None
    var = match_init.group(1)
    start = match_init.group(2).strip()

    # cond:  i < end   or  i <= end
    match_cond = re.match(rf"{re.escape(var)}\s*(<|<=)\s*(.+)", cond_text.strip())
    if not match_cond:
        return None
    op, end = match_cond.group(1), match_cond.group(2).strip()
    if op == "<=":
        # Convert i <= n  →  i < n+1  (keep as expression for now)
        try:
            end = str(int(end) + 1)
        except ValueError:
            end = f"({end}) + 1"

    # incr:  i++  or  i+=n  or  ++i
    step = "1"
    match_step = re.match(
        rf"(?:{re.escape(var)}\s*\+=\s*(.+)|{re.escape(var)}\+\+|\+\+{re.escape(var)})",
        incr_text.strip(),
    )
    if match_step and match_step.group(1):
        step = match_step.group(1).strip()
    elif re.match(rf"{re.escape(var)}\-\-|\-\-{re.escape(var)}", incr_text.strip()):
        step = "-1"
    elif match_step2 := re.match(rf"{re.escape(var)}\s*-=\s*(.+)", incr_text.strip()):
        step = f"-{match_step2.group(1).strip()}"

    return var, start, end, step


def _build_for_c_style(node, src: bytes, lang_tag: str) -> IRNode:
    # tree-sitter-c and tree-sitter-javascript use: initializer, condition, increment
    # tree-sitter-java uses:                        init,        condition, update
    init_node = node.child_by_field_name("initializer") or node.child_by_field_name(
        "init"
    )
    cond_node = node.child_by_field_name("condition")
    incr_node = node.child_by_field_name("increment") or node.child_by_field_name(
        "update"
    )
    body_node = node.child_by_field_name("body")

    init_text = _node_text(init_node, src).strip() if init_node else ""
    cond_text = _node_text(cond_node, src).strip() if cond_node else ""
    incr_text = _node_text(incr_node, src).strip() if incr_node else ""

    body = _parse_block_body(body_node, src, lang_tag) if body_node else []

    parsed = _parse_c_style_for(init_text, cond_text, incr_text)
    if parsed:
        var, start, end, step = parsed
        return IRForRange(var, normalize(start), normalize(end), normalize(step), body)

    # Fallback: store as while loop with raw condition
    return IRWhileLoop(f"{normalize(cond_text)}  /* originally for loop */", body)


def _build_for_python(node, src: bytes) -> IRNode:
    """
    Parse a Python `for i in range(...)` into IRForRange.
    """
    left = node.child_by_field_name("left")
    right = node.child_by_field_name("right")
    body_node = node.child_by_field_name("body")

    var = _node_text(left, src).strip() if left else "i"
    body = _parse_block_body(body_node, src, "python") if body_node else []

    if right:
        right_text = _node_text(right, src).strip()
        # Expect:  range(end)  or  range(start, end)  or  range(start, end, step)
        match = re.match(r"range\((.+)\)$", right_text)
        if match:
            parts = [p.strip() for p in match.group(1).split(",")]
            if len(parts) == 1:
                return IRForRange(var, "0", parts[0], "1", body)
            if len(parts) == 2:
                return IRForRange(var, parts[0], parts[1], "1", body)
            if len(parts) == 3:
                return IRForRange(var, parts[0], parts[1], parts[2], body)

    return IRWhileLoop("True  /* unrecognised for loop */", body)


def _build_while(node, src: bytes, lang_tag: str) -> IRNode:
    cond_node = node.child_by_field_name("condition")
    body_node = node.child_by_field_name("body")
    cond = normalize(_node_text(cond_node, src).strip("( )")) if cond_node else "True"
    body = _parse_block_body(body_node, src, lang_tag) if body_node else []
    return IRWhileLoop(cond, body)


# If statement builder


def _build_if(node, src: bytes, lang_tag: str) -> IRNode:
    cond_node = node.child_by_field_name("condition")
    body_node = node.child_by_field_name("consequence")
    cond = normalize(_node_text(cond_node, src).strip("( )")) if cond_node else "True"
    body = _parse_block_body(body_node, src, lang_tag) if body_node else []
    return IRIfStatement(cond, body)


# Variable builders


def _build_var_js(node, src: bytes) -> List[IRNode]:
    """
    JavaScript: let x = val;  var x = val;  const x = val;
    """

    results = []
    for child in node.children:
        if child.type == "variable_declarator":
            name_node = child.child_by_field_name("name")
            val_node = child.child_by_field_name("value")
            if name_node:
                name = _node_text(name_node, src)
                val = normalize(_node_text(val_node, src)) if val_node else "None"
                results.append(IRVarAssign(name, val, infer_type(val)))
    return results


def _build_var_python(node, src: bytes) -> List[IRNode]:
    """
    Python: name = value
    """

    left_n = node.child_by_field_name("left")
    right_n = node.child_by_field_name("right")
    if not left_n:
        return []
    name = _node_text(left_n, src)
    val = normalize(_node_text(right_n, src)) if right_n else "None"
    return [IRVarAssign(name, val, infer_type(val))]


def _build_var_java(node, src: bytes) -> List[IRNode]:
    """
    Java: int x = 1;  double d = 1.0;
    """

    results = []
    # type is the first child, declarators follow
    for child in node.children:
        if child.type == "variable_declarator":
            name_node = child.child_by_field_name("name")
            value_node = child.child_by_field_name("value")
            if name_node:
                name = _node_text(name_node, src)
                val = normalize(_node_text(value_node, src)) if value_node else "None"
                results.append(IRVarAssign(name, val, infer_type(val)))
    return results


def _build_var_c(node, src: bytes) -> List[IRNode]:
    """
    C: int x = 1;  float y = 1.0;
    """

    results = []
    for child in node.children:
        if child.type in ("init_declarator", "pointer_declarator"):
            name_node = child.child_by_field_name("declarator")
            value_node = child.child_by_field_name("value")
            if name_node:
                name = _node_text(name_node, src)
                val = normalize(_node_text(value_node, src)) if value_node else "None"
                results.append(IRVarAssign(name, val, infer_type(val)))
    return results


# Tree-Sitter Language Parsers

# Could be handled differently but makes determining supported languages easier
_LANG_TO_TS = {
    "javascript": "javascript",
    "python": "python",
    "java": "java",
    "c": "c",
}


def parse_to_ir(source: str, lang: str) -> List[IRNode]:
    """
    Parse source code in `lang` into a flat list of IRNodes.
    """

    if not _TS_AVAILABLE:
        raise RuntimeError(
            "tree_sitter_language_pack is not installed.\nRun:  poetry install"
        )

    ts_lang = _LANG_TO_TS.get(lang.lower())
    if ts_lang is None:
        raise ValueError(f"Unsupported language: {lang}")

    parser = _get_ts_parser(ts_lang)
    src_bytes = source.encode("utf-8")
    tree = parser.parse(src_bytes)

    nodes: List[IRNode] = []
    for child in tree.root_node.children:
        nodes.extend(_dispatch_node(child, src_bytes, ts_lang))

    return nodes
