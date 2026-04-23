"""Tests for the Quine-McCluskey helper module."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import qm


class TestQM(unittest.TestCase):
    def test_implicant_is_equal(self):
        first = qm.Implicant(1, 2)
        same = qm.Implicant(1, 2)
        different = qm.Implicant(2, 2)
        self.assertTrue(first.is_equal(same))
        self.assertFalse(first.is_equal(different))

    def test_differ_by_one_bit(self):
        left = qm.Implicant(0, 0)
        right = qm.Implicant(1, 0)
        can_merge, merged = qm.differ_by_one_bit(left, right)
        self.assertTrue(can_merge)
        self.assertEqual(merged.value, 0)
        self.assertEqual(merged.mask, 1)

        far_apart = qm.Implicant(3, 0)
        can_merge, _ = qm.differ_by_one_bit(left, far_apart)
        self.assertFalse(can_merge)

        different_mask = qm.Implicant(0, 1)
        can_merge, _ = qm.differ_by_one_bit(left, different_mask)
        self.assertFalse(can_merge)

    def test_implicant_covers(self):
        imp = qm.Implicant(0b10, 0b01)
        self.assertTrue(imp.covers(0b10))
        self.assertTrue(imp.covers(0b11))
        self.assertFalse(imp.covers(0b00))
        self.assertFalse(imp.covers(0b01))

    def test_generate_sdnf(self):
        result = qm.generate_sdnf(2, [1, 3], ["A", "B"])
        self.assertEqual(result, "(!A & B) | (A & B)")
        self.assertEqual(qm.generate_sdnf(2, [], ["A", "B"]), "0")

    def test_minimize(self):
        self.assertEqual(qm.minimize(2, [0, 1, 2, 3], None, ["A", "B"]), "1")
        self.assertEqual(qm.minimize(2, [], None, ["A", "B"]), "0")

        result = qm.minimize(3, [0, 1, 2, 5, 6, 7], [3], ["A", "B", "C"])
        self.assertTrue(len(result) > 0)

        result2 = qm.minimize(
            4,
            [0, 1, 2, 5, 6, 7, 8, 9, 10, 14],
            None,
            ["A", "B", "C", "D"],
        )
        self.assertTrue(len(result2) > 0)

    def test_minimize_simple(self):
        result = qm.minimize(2, [1, 3], None, ["A", "B"])
        self.assertEqual(result, "(B)")

    def test_minimize_with_dont_cares(self):
        result = qm.minimize(2, [1], [0], ["A", "B"])
        self.assertEqual(result, "(!A)")

    def test_internal_helpers(self):
        prime_list = qm._find_prime_implicants([0, 1], [])
        self.assertEqual(len(prime_list), 1)
        self.assertIn(qm.Implicant(0, 1), prime_list)

        prime_list = [
            qm.Implicant(0, 1),
            qm.Implicant(2, 1),
            qm.Implicant(0, 0),
        ]
        essentials, remaining = qm._find_essential_primes(prime_list, [0, 2])
        self.assertEqual(len(essentials), 1)
        self.assertEqual(essentials[0], qm.Implicant(2, 1))
        self.assertEqual(remaining, [0])

        solution = qm._cover_remaining([0, 2], prime_list, [])
        self.assertTrue(self._covers_all(solution, [0, 2]))

        best_prime = qm._find_best_prime(prime_list[:2], [0, 1, 2])
        self.assertEqual(best_prime.mask, 1)

        variable_names = ["A", "B"]
        self.assertEqual(
            qm._format_implicant(qm.Implicant(0, 0), 2, variable_names), "(!A & !B)"
        )
        self.assertEqual(
            qm._format_solution([qm.Implicant(0, 0), qm.Implicant(1, 0)], 2, variable_names),
            "(!A & !B) | (!A & B)",
        )

    @staticmethod
    def _covers_all(solution: list[qm.Implicant], minterms: list[int]) -> bool:
        for minterm in minterms:
            if not any(implicant.covers(minterm) for implicant in solution):
                return False
        return True
