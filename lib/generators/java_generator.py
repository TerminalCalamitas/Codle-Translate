import re
from lib.generators.base_generator import BaseGenerator
from lib.ir import (
    IRVarAssign,
    IRPrint,
    IRForRange,
    IRWhileLoop,
    IRIfStatement,
)
from lib.normalize import denormalize

# This acts as a map of the normalized data types to java types
_JAVA_TYPES = {
    "int": "int",
    "float": "double",
    "str": "String",
    "bool": "boolean",
    "unknown": "var",
}


class JavaGenerator(BaseGenerator):
    def _denormalized_expression(self, expr):
        return denormalize(expr, "java")

    def _comment(self, text, pad):
        return f"{pad}// {text}"

    def _var_assign(self, node: IRVarAssign, pad):
        java_type = _JAVA_TYPES.get(node.var_type, "var")
        val = self._denormalized_expression(node.value)

        # Emit augmented assignment for increment/decrement patterns (no type re-declaration)
        match = re.match(rf"^{re.escape(node.name)}\s*\+\s*(\S+)$", node.value)
        if match:
            return f"{pad}{node.name} += {match.group(1)};"

        match = re.match(rf"^{re.escape(node.name)}\s*-\s*(\S+)$", node.value)
        if match:
            return f"{pad}{node.name} -= {match.group(1)};"

        # Java strings need double quotes; single-quoted values get converted
        if node.var_type == "str":
            val = re.sub(r"^'(.*)'$", r'"\1"', val)

        return f"{pad}{java_type} {node.name} = {val};"

    def _print(self, node: IRPrint, pad):
        return f"{pad}System.out.println({self._denormalized_expression(node.value)});"

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

        header = f"{pad}for (int {var} = {start}; {var} < {end}; {incr}) {{"
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
