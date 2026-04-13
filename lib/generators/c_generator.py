import re
from typing import List
from lib.generators.base_generator import BaseGenerator
from lib.ir import (
    IRNode,
    IRVarAssign,
    IRPrint,
    IRForRange,
    IRWhileLoop,
    IRIfStatement,
)
from lib.normalize import denormalize

# This acts as a map of the normalized data types to c types
_C_TYPES = {
    "int": "int",
    "float": "float",
    "str": "char*",
    "bool": "int",
    "unknown": "auto",
}

# C has a more primative output function so output needs to be formatted
_C_FORMAT = {"int": "%d", "float": "%f", "str": "%s", "bool": "%d", "unknown": "%s"}


class CGenerator(BaseGenerator):
    def __init__(self):
        self._needs_stdio = False
        self._needs_bool = False

    def _de(self, expr):
        return denormalize(expr, "c")

    def _comment(self, text, pad):
        return f"{pad}// {text}"

    def _var_assign(self, node: IRVarAssign, pad):
        if node.var_type == "bool":
            self._needs_bool = True
            print(self._needs_bool)
        c_type = _C_TYPES.get(node.var_type, "int")
        val = self._de(node.value)
        # Emit augmented assignment for increment/decrement patterns (no type re-declaration)
        m = re.match(rf"^{re.escape(node.name)}\s*\+\s*(\S+)$", node.value)
        if m:
            return f"{pad}{node.name} += {m.group(1)};"
        m = re.match(rf"^{re.escape(node.name)}\s*-\s*(\S+)$", node.value)
        if m:
            return f"{pad}{node.name} -= {m.group(1)};"
        if node.var_type == "str":
            val = re.sub(r"^'(.*)'$", r'"\1"', val)
        return f"{pad}{c_type} {node.name} = {val};"

    def _print(self, node: IRPrint, pad):
        self._needs_stdio = True
        val = self._de(node.value)
        # If it's a plain string literal, use puts-style printf
        if re.fullmatch(r'"[^"]*"', val):
            return f"{pad}printf({val});"
        return f'{pad}printf("%s\\n", {val});'

    def _for_range(self, node: IRForRange, d, pad):
        v, s, e, st = (
            node.var,
            self._de(node.start),
            self._de(node.end),
            self._de(node.step),
        )
        if st == "1":
            incr = f"{v}++"
        elif st == "-1":
            incr = f"{v}--"
        else:
            incr = f"{v} += {st}"
        header = f"{pad}for (int {v} = {s}; {v} < {e}; {incr}) {{"
        body = self._body(node.body, d + 1)
        return f"{header}\n{body}\n{pad}}}"

    def _while_loop(self, node: IRWhileLoop, d, pad):
        header = f"{pad}while ({self._de(node.condition)}) {{"
        body = self._body(node.body, d + 1)
        return f"{header}\n{body}\n{pad}}}"

    def _if_stmt(self, node: IRIfStatement, d, pad):
        header = f"{pad}if ({self._de(node.condition)}) {{"
        body = self._body(node.body, d + 1)
        return f"{header}\n{body}\n{pad}}}"

    def _c_includes(self, body) -> str:
        if self._needs_bool:
            return "#define true 1 \n#define false 0\n\n" + body

        if self._needs_stdio:
            body = "#include <stdio.h>\n\n" + body

        return body

    def generate(self, nodes: List[IRNode], depth: int = 0) -> str:
        body = super().generate(nodes, depth)

        body = self._c_includes(body)
        return body
