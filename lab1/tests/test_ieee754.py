import unittest
from bitarith.ieee754 import (
    decimal_str_to_ieee754, unpack_ieee754,
    ieee_add, ieee_sub, ieee_mul, ieee_div,
    ieee754_to_decimal_str
)


def bits_str(bits):
    return "".join("1" if b else "0" for b in bits)


class TestIEEE754(unittest.TestCase):
    def test_unpack_validation(self):
        with self.assertRaises(ValueError):
            unpack_ieee754([0] * 31)
        with self.assertRaises(ValueError):
            unpack_ieee754([0] * 31 + [2])

    def test_decimal_to_bits_exact(self):
        # 1.0 => sign 0, exp 127, frac 0
        b1 = decimal_str_to_ieee754("1.0")
        u1 = unpack_ieee754(b1)
        self.assertEqual((u1.sign, u1.exp_field, u1.frac), (0, 127, 0))

        # 2.5 => 1.25 * 2^1 => exp 128, frac 0.25*2^23 = 2097152
        b25 = decimal_str_to_ieee754("2.5")
        u25 = unpack_ieee754(b25)
        self.assertEqual((u25.sign, u25.exp_field, u25.frac), (0, 128, 2097152))

        # -3.75 => -1.875*2^1 => exp 128, frac 0.875*2^23 = 7340032
        b375 = decimal_str_to_ieee754("-3.75")
        u375 = unpack_ieee754(b375)
        self.assertEqual((u375.sign, u375.exp_field, u375.frac), (1, 128, 7340032))

    def test_ops(self):
        b15 = decimal_str_to_ieee754("1.5")
        b225 = decimal_str_to_ieee754("2.25")
        b2 = decimal_str_to_ieee754("2.0")
        b1 = decimal_str_to_ieee754("1.0")

        # 1.5 + 2.25 = 3.75
        r_add = ieee_add(b15, b225)
        self.assertEqual(ieee754_to_decimal_str(r_add, 5)[:5], "3.750")

        # 2.5 - 1.0 = 1.5
        b25 = decimal_str_to_ieee754("2.5")
        r_sub = ieee_sub(b25, b1)
        u = unpack_ieee754(r_sub)
        self.assertEqual((u.sign, u.exp_field, u.frac), (0, 127, 4194304))  # 1.5 => frac 0.5*2^23

        # 1.5 * 2.0 = 3.0
        r_mul = ieee_mul(b15, b2)
        self.assertEqual(ieee754_to_decimal_str(r_mul, 5)[:5], "3.000")

        # 3.0 / 2.0 = 1.5
        b3 = decimal_str_to_ieee754("3.0")
        r_div = ieee_div(b3, b2)
        udiv = unpack_ieee754(r_div)
        self.assertEqual((udiv.sign, udiv.exp_field, udiv.frac), (0, 127, 4194304))
