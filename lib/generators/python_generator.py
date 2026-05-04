import re
from lib.generators.base_generator import BaseGenerator
from lib.ir import (
    IRVarAssign,
    IRPrint,
    IRForRange,
    IRWhileLoop,
    IRIfStatement,
)


class PythonGenerator(BaseGenerator):
    def _comment(self, text, pad):
        return f"{pad}# {text}"

    def _var_assign(self, node: IRVarAssign, pad):
        val = node.value  # already normalized (Python-style)

        # Emit augmented assignment for increment/decrement patterns
        match = re.match(rf"^{re.escape(node.name)}\s*\+\s*(\S+)$", val)
        if match:
            return f"{pad}{node.name} += {match.group(1)}"

        match = re.match(rf"^{re.escape(node.name)}\s*-\s*(\S+)$", val)
        if match:
            return f"{pad}{node.name} -= {match.group(1)}"

        return f"{pad}{node.name} = {val}"

    def _print(self, node: IRPrint, pad):
        return f"{pad}print({node.value})"

    def _for_range(self, node: IRForRange, d, pad):
        step_part = "" if node.step == "1" else f", {node.step}"
        start_part = "" if (node.start == "0" and node.step == 1) else f"{node.start}, "
        header = f"{pad}for {node.var} in range({start_part}{node.end}{step_part}):"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}" if body else f"{header}\n{self.INDENT * (d + 1)}pass"

    def _while_loop(self, node: IRWhileLoop, d, pad):
        header = f"{pad}while {node.condition}:"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}" if body else f"{header}\n{self.INDENT * (d + 1)}pass"

    def _if_stmt(self, node: IRIfStatement, d, pad):
        header = f"{pad}if {node.condition}:"
        body = self._body(node.body, d + 1)

        return f"{header}\n{body}" if body else f"{header}\n{self.INDENT * (d + 1)}pass"
