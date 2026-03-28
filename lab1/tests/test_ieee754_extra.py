import unittest

from bitarith.ieee754 import (
    _cmp_scaled_pow2,
    _find_binary_exponent,
    _pack_from_significand_exp2,
    _parse_decimal_to_rational,
    _unpack_to_sig_exp2,
    decimal_str_to_ieee754,
    ieee_add,
    ieee_div,
    ieee_mul,
    ieee754_to_decimal_str,
    ieee754_to_rational,
    pack_ieee754,
    unpack_ieee754,
)


class TestIEEE754Extra(unittest.TestCase):
    def test_pack_validation_errors(self):
        with self.assertRaises(ValueError):
            pack_ieee754(2, 0, 0)
        with self.assertRaises(ValueError):
            pack_ieee754(0, 256, 0)
        with self.assertRaises(ValueError):
            pack_ieee754(0, 0, 1 << 23)

    def test_rational_and_decimal_special_cases(self):
        nan_bits = pack_ieee754(0, 255, 1)
        inf_bits = pack_ieee754(0, 255, 0)
        ninf_bits = pack_ieee754(1, 255, 0)
        sub_bits = pack_ieee754(0, 0, 1)
        normal_bits = pack_ieee754(0, 127, 0)

        self.assertEqual(ieee754_to_rational(nan_bits), (0, 0, -1))
        self.assertEqual(ieee754_to_rational(inf_bits), (0, 1, -1))
        self.assertEqual(ieee754_to_rational(sub_bits), (0, 1, 149))
        self.assertEqual(ieee754_to_rational(normal_bits), (0, 1 << 23, 23))

        self.assertEqual(ieee754_to_decimal_str(nan_bits), "NaN")
        self.assertEqual(ieee754_to_decimal_str(inf_bits), "Inf")
        self.assertEqual(ieee754_to_decimal_str(ninf_bits), "-Inf")
        self.assertEqual(ieee754_to_decimal_str(pack_ieee754(0, 0, 0)), "0.0")

    def test_parse_decimal_to_rational_errors_and_exponent(self):
        self.assertEqual(_parse_decimal_to_rational(" +001.2300e+2 "), (0, 12300, 2))
        self.assertEqual(_parse_decimal_to_rational("-1.2e-2"), (1, 12, 3))

        for bad in ["", "   ", "+", "e1", "1e", "1e+", "1e-", "1e+X", ".", "-."]:
            with self.assertRaises(ValueError):
                _parse_decimal_to_rational(bad)

    def test_scaled_pow2_and_exponent_search(self):
        self.assertEqual(_cmp_scaled_pow2(4, 0, 2), 0)
        self.assertEqual(_cmp_scaled_pow2(3, 0, 2), -1)
        self.assertEqual(_cmp_scaled_pow2(5, 0, 2), 1)
        self.assertEqual(_cmp_scaled_pow2(1, 0, -1), 1)
        self.assertEqual(_cmp_scaled_pow2(1, 1, -1), -1)

        self.assertEqual(_find_binary_exponent(3, 0), 1)
        self.assertEqual(_find_binary_exponent(1, 1), -4)

    def test_decimal_to_ieee754_extremes(self):
        pos_zero = decimal_str_to_ieee754("0")
        self.assertEqual(unpack_ieee754(pos_zero).is_zero(), True)

        neg_zero = decimal_str_to_ieee754("-0")
        uz = unpack_ieee754(neg_zero)
        self.assertEqual((uz.sign, uz.exp_field, uz.frac), (1, 0, 0))

        ov = unpack_ieee754(decimal_str_to_ieee754("1e50"))
        self.assertTrue(ov.is_inf())

        sub = unpack_ieee754(decimal_str_to_ieee754("1e-45"))
        self.assertTrue(sub.is_subnormal() or sub.is_zero())

    def test_pack_from_significand_exp2_branches(self):
        self.assertEqual(unpack_ieee754(_pack_from_significand_exp2(0, 0, 0)).is_zero(), True)

        huge = unpack_ieee754(_pack_from_significand_exp2(0, 1 << 40, 100))
        self.assertTrue(huge.is_inf())

        normal = unpack_ieee754(_pack_from_significand_exp2(0, 1 << 23, -23))
        self.assertTrue(normal.is_normal())

        sub = unpack_ieee754(_pack_from_significand_exp2(0, 1, -149))
        self.assertTrue(sub.is_subnormal() or sub.is_normal())

        tiny = unpack_ieee754(_pack_from_significand_exp2(0, 1, -200))
        self.assertTrue(tiny.is_zero())

    def test_unpack_kinds(self):
        self.assertEqual(_unpack_to_sig_exp2(pack_ieee754(0, 255, 1))[3], "nan")
        self.assertEqual(_unpack_to_sig_exp2(pack_ieee754(0, 255, 0))[3], "inf")
        self.assertEqual(_unpack_to_sig_exp2(pack_ieee754(0, 0, 0))[3], "zero")
        self.assertEqual(_unpack_to_sig_exp2(pack_ieee754(0, 0, 3))[3], "sub")
        self.assertEqual(_unpack_to_sig_exp2(pack_ieee754(0, 127, 0))[3], "norm")

    def test_add_mul_div_special_paths(self):
        nan = pack_ieee754(0, 255, 1)
        inf = pack_ieee754(0, 255, 0)
        ninf = pack_ieee754(1, 255, 0)
        zero = pack_ieee754(0, 0, 0)
        one = decimal_str_to_ieee754("1.0")
        two = decimal_str_to_ieee754("2.0")

        self.assertTrue(unpack_ieee754(ieee_add(nan, one)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_add(inf, ninf)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_add(one, inf)).is_inf())
        self.assertEqual(ieee_add(zero, one), one)
        self.assertEqual(ieee_add(one, zero), one)

        self.assertTrue(unpack_ieee754(ieee_mul(nan, one)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_mul(inf, zero)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_mul(inf, one)).is_inf())
        self.assertTrue(unpack_ieee754(ieee_mul(zero, one)).is_zero())

        self.assertTrue(unpack_ieee754(ieee_div(nan, one)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_div(inf, inf)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_div(inf, one)).is_inf())
        self.assertTrue(unpack_ieee754(ieee_div(one, inf)).is_zero())
        self.assertTrue(unpack_ieee754(ieee_div(zero, zero)).is_nan())
        self.assertTrue(unpack_ieee754(ieee_div(one, zero)).is_inf())
        self.assertTrue(unpack_ieee754(ieee_div(zero, one)).is_zero())

        div = ieee_div(decimal_str_to_ieee754("3.0"), two)
        self.assertEqual(ieee754_to_decimal_str(div, 5)[:5], "1.500")


if __name__ == "__main__":
    unittest.main()
