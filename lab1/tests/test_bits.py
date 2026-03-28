import unittest
from bitarith.bits import int_to_bits_unsigned, bits_to_int_unsigned, add_bits, increment_bits, rshift_round_nearest_even


class TestBits(unittest.TestCase):
    def test_roundtrip_unsigned(self):
        for n in [0, 1, 2, 3, 5, 255, 256, 1024, 2**32 - 1]:
            bits = int_to_bits_unsigned(n, 32)
            self.assertEqual(bits_to_int_unsigned(bits), n)

    def test_add_bits(self):
        a = int_to_bits_unsigned(5, 8)   # 00000101
        b = int_to_bits_unsigned(13, 8)  # 00001101
        s, c = add_bits(a, b)
        self.assertEqual(bits_to_int_unsigned(s), 18)
        self.assertEqual(c, 0)

    def test_increment(self):
        x = int_to_bits_unsigned(255, 8)
        y, c = increment_bits(x)
        self.assertEqual(bits_to_int_unsigned(y), 0)
        self.assertEqual(c, 1)

    def test_rshift_round_nearest_even(self):
        # 7/2 = 3.5 => nearest-even is 4
        self.assertEqual(rshift_round_nearest_even(7, 1), 4)
        # 5/2=2.5 => nearest-even is 2
        self.assertEqual(rshift_round_nearest_even(5, 1), 2)
