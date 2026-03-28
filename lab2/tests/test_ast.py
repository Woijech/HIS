from __future__ import annotations

import unittest

from logiclab.domain.ast import BinaryOp, Constant, UnaryOp, Variable


class AstTests(unittest.TestCase):
    def test_constant_evaluates_to_its_value(self) -> None:
        self.assertEqual(Constant(1).evaluate({}), 1)

    def test_variable_reads_value_from_context(self) -> None:
        self.assertEqual(Variable('a').evaluate({'a': 0}), 0)

    def test_variable_reports_its_name(self) -> None:
        self.assertEqual(Variable('a').variables(), {'a'})

    def test_unary_not_inverts_operand(self) -> None:
        self.assertEqual(UnaryOp('!', Variable('a')).evaluate({'a': 0}), 1)

    def test_binary_operations_follow_boolean_rules(self) -> None:
        cases = (
            ('&', {'a': 1, 'b': 1}, 1),
            ('|', {'a': 0, 'b': 1}, 1),
            ('->', {'a': 1, 'b': 0}, 0),
            ('~', {'a': 1, 'b': 1}, 1),
        )

        for op, values, expected in cases:
            with self.subTest(op=op):
                expr = BinaryOp(op, Variable('a'), Variable('b'))
                self.assertEqual(expr.evaluate(values), expected)

    def test_invalid_unary_operation_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            UnaryOp('?', Variable('a')).evaluate({'a': 1})

    def test_invalid_binary_operation_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            BinaryOp('?', Variable('a'), Variable('b')).evaluate({'a': 1, 'b': 0})
