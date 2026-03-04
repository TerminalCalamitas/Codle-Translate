from typing import List
from lib.ir import (
    IRNode,
    IRComment,
    IRVarAssign,
    IRPrint,
    IRForRange,
    IRWhileLoop,
    IRIfStatement,
)


class BaseGenerator:
    INDENT = "    "

    def generate(self, nodes: List[IRNode], depth: int = 0) -> str:
        lines = []
        for node in nodes:
            lines.append(self._emit(node, depth))
        return "\n".join(lines)

    def _emit(self, node: IRNode, depth: int) -> str:
        pad = self.INDENT * depth
        if isinstance(node, IRComment):
            return self._comment(node.text, pad)
        if isinstance(node, IRVarAssign):
            return self._var_assign(node, pad)
        if isinstance(node, IRPrint):
            return self._print(node, pad)
        if isinstance(node, IRForRange):
            return self._for_range(node, depth, pad)
        if isinstance(node, IRWhileLoop):
            return self._while_loop(node, depth, pad)
        if isinstance(node, IRIfStatement):
            return self._if_stmt(node, depth, pad)
        return f"{pad}// [unhandled node: {type(node).__name__}]"

    # Subclasses override these
    def _comment(self, text, pad):
        raise NotImplementedError

    def _var_assign(self, node, pad):
        raise NotImplementedError

    def _print(self, node, pad):
        raise NotImplementedError

    def _for_range(self, node, d, pad):
        raise NotImplementedError

    def _while_loop(self, node, d, pad):
        raise NotImplementedError

    def _if_stmt(self, node, d, pad):
        raise NotImplementedError

    def _body(self, nodes, depth):
        return self.generate(nodes, depth)
