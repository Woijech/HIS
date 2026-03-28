import unittest

from bitarith.int_codes import (
    int_to_sign_magnitude,
    ones_complement_to_int,
    sign_magnitude_to_int,
    twos_abs,
    twos_compare,
    twos_complement_to_int,
    int_to_twos_complement,
)


class TestIntCodesExtra(unittest.TestCase):
    def test_sign_magnitude_wrap_and_errors(self):
        wrapped = int_to_sign_magnitude(2**31)
        self.assertEqual(sign_magnitude_to_int(wrapped), 0)

        with self.assertRaises(ValueError):
            sign_magnitude_to_int([0] * 31)

    def test_ones_complement_edge_cases(self):
        self.assertEqual(ones_complement_to_int([1] * 32), 0)
        with self.assertRaises(ValueError):
            ones_complement_to_int([0] * 31)

    def test_twos_helpers(self):
        pos_bits = int_to_twos_complement(42)
        neg_bits = int_to_twos_complement(-42)

        abs_pos, sign_pos = twos_abs(pos_bits)
        abs_neg, sign_neg = twos_abs(neg_bits)

        self.assertEqual(sign_pos, 0)
        self.assertEqual(sign_neg, 1)
        self.assertEqual(twos_complement_to_int(abs_pos), 42)
        self.assertEqual(twos_complement_to_int(abs_neg), 42)

    def test_twos_compare_branches(self):
        self.assertEqual(twos_compare(int_to_twos_complement(-1), int_to_twos_complement(1)), -1)
        self.assertEqual(twos_compare(int_to_twos_complement(5), int_to_twos_complement(2)), 1)
        self.assertEqual(twos_compare(int_to_twos_complement(-5), int_to_twos_complement(-2)), -1)
        self.assertEqual(twos_compare(int_to_twos_complement(-5), int_to_twos_complement(-5)), 0)


if __name__ == "__main__":
    unittest.main()
