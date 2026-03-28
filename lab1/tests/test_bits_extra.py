import unittest

from bitarith.bits import (
    Bits32,
    _validate_bit,
    _validate_bits,
    bitwise_and,
    bitwise_not,
    bitwise_xor,
    compare_bits_unsigned,
    shift_left,
    shift_right,
    shift_right_with_sticky_int,
)


class TestBitsExtra(unittest.TestCase):
    def test_validate_bit_and_bits_errors(self):
        with self.assertRaises(ValueError):
            _validate_bit(2)
        with self.assertRaises(ValueError):
            _validate_bits([0, 1], 3)
        with self.assertRaises(ValueError):
            _validate_bits([0, 1, 2], 3)

    def test_bitwise_ops_and_length_mismatch(self):
        self.assertEqual(bitwise_not([0, 1, 0]), [1, 0, 1])
        self.assertEqual(bitwise_and([1, 0, 1], [1, 1, 0]), [1, 0, 0])
        self.assertEqual(bitwise_xor([1, 0, 1], [1, 1, 0]), [0, 1, 1])

        with self.assertRaises(ValueError):
            bitwise_and([1], [1, 0])
        with self.assertRaises(ValueError):
            bitwise_xor([1], [1, 0])

    def test_compare_and_shifts(self):
        self.assertEqual(compare_bits_unsigned([0, 1], [0, 1]), 0)
        self.assertEqual(compare_bits_unsigned([0, 1], [1, 0]), -1)
        self.assertEqual(compare_bits_unsigned([1, 0], [0, 1]), 1)
        with self.assertRaises(ValueError):
            compare_bits_unsigned([1], [1, 0])

        self.assertEqual(shift_left([1, 0, 1, 1], 2), [1, 1, 0, 0])
        self.assertEqual(shift_left([1, 0, 1, 1], 4), [0, 0, 0, 0])
        self.assertEqual(shift_right([1, 0, 1, 1], 2), [0, 0, 1, 0])
        self.assertEqual(shift_right([1, 0, 1, 1], 4), [0, 0, 0, 0])

        with self.assertRaises(ValueError):
            shift_left([1, 0], -1)
        with self.assertRaises(ValueError):
            shift_right([1, 0], -1)

    def test_sticky_shift_and_bits32_helpers(self):
        self.assertEqual(shift_right_with_sticky_int(13, 0), 13)
        self.assertEqual(shift_right_with_sticky_int(0, 5), 0)
        self.assertEqual(shift_right_with_sticky_int(13, 2), 3)
        self.assertEqual(shift_right_with_sticky_int(13, 100), 1)

        b = Bits32.from_unsigned_int(5)
        self.assertEqual(b.to_unsigned_int(), 5)
        self.assertEqual(len(b.to_list()), 32)
        self.assertTrue(str(b).endswith("0101"))

        b2 = Bits32.from_list([0] * 32)
        self.assertEqual(b2.to_unsigned_int(), 0)

        with self.assertRaises(ValueError):
            Bits32.from_list([0] * 31)


if __name__ == "__main__":
    unittest.main()
