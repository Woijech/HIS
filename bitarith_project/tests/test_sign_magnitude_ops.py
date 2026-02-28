import unittest
from bitarith.sign_magnitude_ops import signmag_multiply, signmag_divide_fixed5


class TestSignMagnitudeOps(unittest.TestCase):
    def test_multiply_basic(self):
        r = signmag_multiply(-7, 6)
        self.assertEqual(r.decimal, -42)

    def test_divide_fixed5(self):
        r = signmag_divide_fixed5(1, 2)
        self.assertEqual(r.as_float_str, "0.50000")
        r2 = signmag_divide_fixed5(-3, 2)
        self.assertEqual(r2.as_float_str, "-1.50000")

    def test_div_by_zero(self):
        r = signmag_divide_fixed5(1, 0)
        self.assertTrue(r.div_by_zero)
        self.assertEqual(r.as_float_str, "NaN")
