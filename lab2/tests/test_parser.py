from __future__ import annotations

import unittest

from logiclab.domain.ast import BinaryOp, UnaryOp, Variable
from logiclab.domain.parser import ExpressionSyntaxError, normalize_expression, parse_expression, tokenize


class ParserTests(unittest.TestCase):
    def test_normalization_replaces_unicode_symbols(self) -> None:
        self.assertEqual(normalize_expression('¬a ∨ b → c'), '!a | b -> c')

    def test_parse_expression_respects_operator_precedence(self) -> None:
        expr = parse_expression('a|b&!c')
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, '|')
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, '&')
        self.assertIsInstance(expr.right.right, UnaryOp)

    def test_parse_expression_treats_implication_as_right_associative(self) -> None:
        expr = parse_expression('a->b->c')
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, '->')
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, '->')

    def test_invalid_symbol_raises_error(self) -> None:
        with self.assertRaises(ExpressionSyntaxError):
            tokenize('a + b')

    def test_parentheses_are_supported(self) -> None:
        expr = parse_expression('(a&b)|c')
        self.assertEqual(expr.evaluate({'a': 1, 'b': 1, 'c': 0}), 1)
        self.assertEqual(expr.evaluate({'a': 0, 'b': 1, 'c': 0}), 0)

    def test_equivalence_is_supported(self) -> None:
        expr = parse_expression('a~b')
        self.assertEqual(expr.evaluate({'a': 0, 'b': 0}), 1)
        self.assertEqual(expr.evaluate({'a': 1, 'b': 0}), 0)

    def test_extra_token_raises_error(self) -> None:
        with self.assertRaises(ExpressionSyntaxError):
            parse_expression('a b')

    def test_unexpected_token_raises_error(self) -> None:
        with self.assertRaises(ExpressionSyntaxError):
            parse_expression('()')
