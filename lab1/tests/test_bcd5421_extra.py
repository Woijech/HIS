import unittest

from bitarith.bcd5421 import add_5421_bcd, decode_5421_bcd, encode_5421_bcd


class TestBCD5421Extra(unittest.TestCase):
    def test_encode_errors(self):
        with self.assertRaises(ValueError):
            encode_5421_bcd("")
        with self.assertRaises(ValueError):
            encode_5421_bcd("12a")
        with self.assertRaises(ValueError):
            encode_5421_bcd("123456789")

    def test_decode_errors(self):
        with self.assertRaises(ValueError):
            decode_5421_bcd([0] * 31)

        bits = [0] * 32
        bits[0:4] = [1, 1, 1, 1]
        with self.assertRaises(ValueError):
            decode_5421_bcd(bits)

    def test_add_errors(self):
        bad = [0] * 32
        bad[0:4] = [1, 1, 1, 1]
        ok = encode_5421_bcd("1")
        with self.assertRaises(ValueError):
            add_5421_bcd(bad, ok)


if __name__ == "__main__":
    unittest.main()
