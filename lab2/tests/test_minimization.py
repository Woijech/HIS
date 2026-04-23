from __future__ import annotations

import unittest

from logiclab.domain.analysis import analyze_expression, selected_implicants_to_cnf, selected_implicants_to_dnf
from logiclab.domain.minimization import combine_patterns, index_to_bits, minimize_minterms


class MinimizationTests(unittest.TestCase):
    def test_combine_patterns_merges_terms_with_single_difference(self) -> None:
        self.assertEqual(combine_patterns((1, 0, 0), (1, 0, 1)), (1, 0, None))

    def test_combine_patterns_rejects_incompatible_terms(self) -> None:
        self.assertIsNone(combine_patterns((1, None, 0), (1, 1, 1)))

    def test_selected_implicants_are_rendered_as_expected_dnf(self) -> None:
        result = analyze_expression('(!a&b&c)|(a&!b&!c)|(a&!b&c)|(a&b&!c)|(a&b&c)')
        minimized = selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables)
        self.assertEqual(minimized, 'a | (b & c)')

    def test_minimize_minterms_returns_empty_result_for_empty_function(self) -> None:
        minimized = minimize_minterms((), 3)
        self.assertEqual(minimized.selected_implicants, ())
        self.assertEqual(minimized.chart, {})

    def test_analyze_expression_exposes_prime_chart_for_each_minterm(self) -> None:
        result = analyze_expression('a|b')
        chart_keys = tuple(sorted(result.minimization.chart))
        self.assertEqual(chart_keys, (1, 2, 3))
        minimized = selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables)
        self.assertEqual(set(minimized.split(' | ')), {'a', 'b'})

    def test_tautology_minimizes_to_one(self) -> None:
        result = analyze_expression('a|!a')
        minimized = selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables)
        self.assertEqual(minimized, '1')

    def test_selected_implicants_are_rendered_as_expected_cnf(self) -> None:
        result = analyze_expression('a&b')
        minimized = selected_implicants_to_cnf(result.maxterm_minimization.selected_implicants, result.variables)
        self.assertEqual(minimized, 'a & b')

    def test_minimize_minterms_returns_cover_for_all_requested_minterms(self) -> None:
        result = minimize_minterms((0, 1, 2, 5, 6), 3)
        self.assertEqual(len(result.selected_implicants), 3)
        covered = set()
        for implicant in result.selected_implicants:
            covered.update(implicant.covered)
        self.assertEqual(covered, {0, 1, 2, 5, 6})
