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


class JavaScriptGenerator(BaseGenerator):
    def _de(self, expr):
        return denormalize(expr, "javascript")

    def _comment(self, text, pad):
        return f"{pad}// {text}"

    def _var_assign(self, node: IRVarAssign, pad):
        val = self._de(node.value)
        # Emit augmented assignment for increment/decrement patterns (no `let` re-declaration)
        m = re.match(rf"^{re.escape(node.name)}\s*\+\s*(\S+)$", node.value)
        if m:
            return f"{pad}{node.name} += {m.group(1)};"
        m = re.match(rf"^{re.escape(node.name)}\s*-\s*(\S+)$", node.value)
        if m:
            return f"{pad}{node.name} -= {m.group(1)};"
        return f"{pad}let {node.name} = {val};"

    def _print(self, node: IRPrint, pad):
        return f"{pad}console.log({self._de(node.value)});"

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
        header = f"{pad}for (let {v} = {s}; {v} < {e}; {incr}) {{"
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
