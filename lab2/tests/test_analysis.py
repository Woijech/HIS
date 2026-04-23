from __future__ import annotations

import unittest

from logiclab.domain.analysis import (
    analyze_expression,
    build_canonical_forms,
    evaluate_expression,
)
from logiclab.domain.parser import parse_expression


class AnalysisTests(unittest.TestCase):
    def test_evaluate_expression_builds_truth_table_in_binary_order(self) -> None:
        expr = parse_expression('a|b')
        rows = evaluate_expression(expr, ('a', 'b'))
        self.assertEqual([row.result for row in rows], [0, 1, 1, 1])

    def test_build_canonical_forms_for_or_expression(self) -> None:
        expr = parse_expression('a|b')
        rows = evaluate_expression(expr, ('a', 'b'))
        canonical = build_canonical_forms(rows, ('a', 'b'))
        self.assertEqual(canonical.minterms, (1, 2, 3))
        self.assertEqual(canonical.maxterms, (0,))
        self.assertEqual(canonical.index_binary, '0111')
        self.assertEqual(canonical.index_decimal, 7)

    def test_analyze_expression_calculates_post_classes_for_xor(self) -> None:
        result = analyze_expression('(!a&b)|(a&!b)')
        self.assertTrue(result.post_classes.t0)
        self.assertFalse(result.post_classes.t1)
        self.assertFalse(result.post_classes.m)
        self.assertTrue(result.post_classes.l)

    def test_analyze_expression_builds_zhegalkin_polynomial_for_xor(self) -> None:
        result = analyze_expression('(!a&b)|(a&!b)')
        self.assertEqual(result.zhegalkin, 'b ⊕ a')

    def test_analyze_expression_detects_fictive_variable(self) -> None:
        result = analyze_expression('a|!a')
        self.assertEqual(result.fictive_variables, ('a',))
        self.assertEqual(result.canonical.sdnf, '(!a) | (a)')

    def test_analyze_expression_builds_boolean_derivatives(self) -> None:
        result = analyze_expression('a&b')
        derivatives = {item.variables: item for item in result.derivatives}
        self.assertEqual(derivatives[('a',)].remaining_variables, ('b',))
        self.assertEqual(derivatives[('a',)].index_binary, '01')
        self.assertEqual(derivatives[('a',)].sdnf, '(b)')
        self.assertEqual(derivatives[('b',)].remaining_variables, ('a',))
        self.assertEqual(derivatives[('b',)].index_binary, '01')
        self.assertEqual(derivatives[('b',)].sdnf, '(a)')
        self.assertEqual(derivatives[('a', 'b')].remaining_variables, ())
        self.assertEqual(derivatives[('a', 'b')].index_binary, '1')
        self.assertEqual(derivatives[('a', 'b')].sdnf, '1')

    def test_analyze_expression_supports_constant_expression(self) -> None:
        result = analyze_expression('1')
        self.assertEqual(result.canonical.index_binary, '1')
        self.assertEqual(result.canonical.index_decimal, 1)
        self.assertEqual(result.zhegalkin, '1')
