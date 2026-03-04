from dataclasses import dataclass
from typing import List, Union


@dataclass
class IRComment:
    text: str  # string value without quotes or leading comment symbols


@dataclass
class IRVarAssign:
    name: str
    value: str  # normalized value string
    var_type: str


@dataclass
class IRPrint:
    value: str  # normalized argument string


@dataclass
class IRForRange:
    """
    A C-style for loop reduced to a range triple
    """

    var: str
    start: str  # inclusive lower bound expression
    end: str  # exclusive upper bound expression
    step: str  # step expression
    body: List["IRNode"]


@dataclass
class IRWhileLoop:
    condition: str  # normalized condition string
    body: List["IRNode"]


@dataclass
class IRIfStatement:
    condition: str  # normalized condition string
    body: List["IRNode"]


IRNode = Union[IRComment, IRVarAssign, IRPrint, IRForRange, IRWhileLoop, IRIfStatement]
