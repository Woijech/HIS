import unittest
from bitarith.int_codes import (
    int_to_sign_magnitude, sign_magnitude_to_int,
    int_to_ones_complement, ones_complement_to_int,
    int_to_twos_complement, twos_complement_to_int,
    twos_add, twos_subtract, twos_negate
)
from bitarith.bits import bits_to_int_unsigned


class TestIntCodes(unittest.TestCase):
    def test_sign_magnitude_roundtrip(self):
        for n in [0, 1, -1, 2, -2, 12345, -54321, 2**31 - 1, -(2**31 - 1)]:
            bits = int_to_sign_magnitude(n)
            self.assertEqual(sign_magnitude_to_int(bits), n)

    def test_ones_complement_roundtrip(self):
        for n in [0, 1, -1, 2, -2, 12345, -54321]:
            bits = int_to_ones_complement(n)
            self.assertEqual(ones_complement_to_int(bits), n)

    def test_twos_complement_roundtrip(self):
        for n in [0, 1, -1, 2, -2, 12345, -54321, 2**31 - 1, -(2**31)]:
            bits = int_to_twos_complement(n)
            self.assertEqual(twos_complement_to_int(bits), n)

    def test_twos_add_wrap(self):
        a = int_to_twos_complement(2**31 - 1)
        b = int_to_twos_complement(1)
        s = twos_add(a, b)
        self.assertEqual(twos_complement_to_int(s), -(2**31))

    def test_twos_subtract(self):
        a = int_to_twos_complement(10)
        b = int_to_twos_complement(3)
        r = twos_subtract(a, b)
        self.assertEqual(twos_complement_to_int(r), 7)

    def test_twos_negate(self):
        x = int_to_twos_complement(123)
        nx = twos_negate(x)
        self.assertEqual(twos_complement_to_int(nx), -123)
