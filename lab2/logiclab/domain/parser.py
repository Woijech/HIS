from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .ast import BinaryOp, Constant, Expr, UnaryOp, Variable


_ALLOWED_VARS = {'a', 'b', 'c', 'd', 'e'}
_UNICODE_REPLACEMENTS = {
    '¬': '!',
    '∧': '&',
    '∨': '|',
    '→': '->',
    '⇒': '->',
    '↔': '~',
    '≡': '~',
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


class ExpressionSyntaxError(ValueError):
    pass


def normalize_expression(text: str) -> str:
    normalized = text
    for source, target in _UNICODE_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)
    return normalized.strip().lower()


def tokenize(text: str) -> List[Token]:
    text = normalize_expression(text)
    tokens: List[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in '()!&|~':
            tokens.append(Token(ch, ch))
            i += 1
            continue
        if ch == '-' and i + 1 < len(text) and text[i + 1] == '>':
            tokens.append(Token('->', '->'))
            i += 2
            continue
        if ch in _ALLOWED_VARS:
            tokens.append(Token('VAR', ch))
            i += 1
            continue
        if ch in '01':
            tokens.append(Token('CONST', ch))
            i += 1
            continue
        raise ExpressionSyntaxError(f'Недопустимый символ: {ch!r}')
    tokens.append(Token('EOF', 'EOF'))
    return tokens


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._position = 0

    @property
    def current(self) -> Token:
        return self._tokens[self._position]

    def consume(self, kind: str | None = None) -> Token:
        token = self.current
        if kind is not None and token.kind != kind:
            raise ExpressionSyntaxError(
                f'Ожидался токен {kind!r}, получен {token.kind!r}'
            )
        self._position += 1
        return token

    def parse(self) -> Expr:
        expr = self.parse_equivalence()
        if self.current.kind != 'EOF':
            raise ExpressionSyntaxError(f'Лишний токен: {self.current.value!r}')
        return expr

    def parse_equivalence(self) -> Expr:
        left = self.parse_implication()
        while self.current.kind == '~':
            self.consume('~')
            right = self.parse_implication()
            left = BinaryOp('~', left, right)
        return left

    def parse_implication(self) -> Expr:
        left = self.parse_or()
        if self.current.kind == '->':
            self.consume('->')
            right = self.parse_implication()
            return BinaryOp('->', left, right)
        return left

    def parse_or(self) -> Expr:
        left = self.parse_and()
        while self.current.kind == '|':
            self.consume('|')
            right = self.parse_and()
            left = BinaryOp('|', left, right)
        return left

    def parse_and(self) -> Expr:
        left = self.parse_not()
        while self.current.kind == '&':
            self.consume('&')
            right = self.parse_not()
            left = BinaryOp('&', left, right)
        return left

    def parse_not(self) -> Expr:
        if self.current.kind == '!':
            self.consume('!')
            return UnaryOp('!', self.parse_not())
        return self.parse_atom()

    def parse_atom(self) -> Expr:
        token = self.current
        if token.kind == 'VAR':
            self.consume('VAR')
            return Variable(token.value)
        if token.kind == 'CONST':
            self.consume('CONST')
            return Constant(int(token.value))
        if token.kind == '(':
            self.consume('(')
            expr = self.parse_equivalence()
            self.consume(')')
            return expr
        raise ExpressionSyntaxError(f'Неожиданный токен: {token.value!r}')


def parse_expression(text: str) -> Expr:
    return Parser(tokenize(text)).parse()
