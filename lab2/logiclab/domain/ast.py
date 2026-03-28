from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Set


class Expr:
    def evaluate(self, values: Mapping[str, int]) -> int:
        raise NotImplementedError

    def variables(self) -> Set[str]:
        raise NotImplementedError


@dataclass(frozen=True)
class Constant(Expr):
    value: int

    def evaluate(self, values: Mapping[str, int]) -> int:
        return int(self.value)

    def variables(self) -> Set[str]:
        return set()


@dataclass(frozen=True)
class Variable(Expr):
    name: str

    def evaluate(self, values: Mapping[str, int]) -> int:
        return int(values[self.name])

    def variables(self) -> Set[str]:
        return {self.name}


@dataclass(frozen=True)
class UnaryOp(Expr):
    op: str
    operand: Expr

    def evaluate(self, values: Mapping[str, int]) -> int:
        if self.op != '!':
            raise ValueError(f'Unsupported unary op: {self.op}')
        return 1 - self.operand.evaluate(values)

    def variables(self) -> Set[str]:
        return self.operand.variables()


@dataclass(frozen=True)
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr

    def evaluate(self, values: Mapping[str, int]) -> int:
        a = self.left.evaluate(values)
        b = self.right.evaluate(values)
        if self.op == '&':
            return a & b
        if self.op == '|':
            return a | b
        if self.op == '->':
            return (1 - a) | b
        if self.op == '~':
            return int(a == b)
        raise ValueError(f'Unsupported binary op: {self.op}')

    def variables(self) -> Set[str]:
        return self.left.variables() | self.right.variables()
