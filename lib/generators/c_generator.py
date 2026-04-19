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


class CGenerator(BaseGenerator):
    def __init__(self):
        self._needs_stdio = False
        self._needs_bool = False

    def _denormalized_expression(self, expr):
        return denormalize(expr, "c")

    def _comment(self, text, pad):
        return f"{pad}// {text}"

    def _var_assign(self, node: IRVarAssign, pad):
        if node.var_type == "bool":
            self._needs_bool = True
            print(self._needs_bool)

        c_type = _C_TYPES.get(node.var_type, "int")
        val = self._denormalized_expression(node.value)

        # Emit augmented assignment for increment/decrement patterns (no type re-declaration)
        match = re.match(rf"^{re.escape(node.name)}\s*\+\s*(\S+)$", node.value)
        if match:
            return f"{pad}{node.name} += {match.group(1)};"

        match = re.match(rf"^{re.escape(node.name)}\s*-\s*(\S+)$", node.value)
        if match:
            return f"{pad}{node.name} -= {match.group(1)};"

        if node.var_type == "str":
            val = re.sub(r"^'(.*)'$", r'"\1"', val)

        return f"{pad}{c_type} {node.name} = {val};"

    def _print(self, node: IRPrint, pad):
        self._needs_stdio = True
        val = self._denormalized_expression(node.value)

        # If it's a plain string literal, use puts-style printf
        if re.fullmatch(r'"[^"]*"', val):
            return f"{pad}printf({val});"

        return f'{pad}printf("%s\\n", {val});'

    def _for_range(self, node: IRForRange, d, pad):
        var, start, end, step = (
            node.var,
            self._denormalized_expression(node.start),
            self._denormalized_expression(node.end),
            self._denormalized_expression(node.step),
        )

        if step == "1":
            incr = f"{var}++"
        elif step == "-1":
            incr = f"{var}--"
        else:
            incr = f"{var} += {step}"

        header = f"{pad}for (let {var} = {start}; {var} < {end}; {incr}) {{"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}\n{pad}}}"

    def _while_loop(self, node: IRWhileLoop, d, pad):
        header = f"{pad}while ({self._denormalized_expression(node.condition)}) {{"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}\n{pad}}}"

    def _if_stmt(self, node: IRIfStatement, d, pad):
        header = f"{pad}if ({self._denormalized_expression(node.condition)}) {{"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}\n{pad}}}"

    def _c_includes(self, body) -> str:
        if self._needs_bool:
            body = "#define true 1 \n#define false 0\n\n" + body

        if self._needs_stdio:
            body = "#include <stdio.h>\n\n" + body

        return body

    def generate(self, nodes: List[IRNode], depth: int = 0) -> str:
        body = super().generate(nodes, depth)

        body = self._c_includes(body)
        return body
