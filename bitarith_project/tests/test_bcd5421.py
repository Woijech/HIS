import unittest
from bitarith.bcd5421 import encode_5421_bcd, decode_5421_bcd, add_5421_bcd


class TestBCD5421(unittest.TestCase):
    def test_encode_decode(self):
        for s in ["0", "1", "9", "10", "12345678", "00001234"]:
            bits = encode_5421_bcd(s)
            self.assertEqual(decode_5421_bcd(bits), str(int(s)))  # normalize

    def test_add(self):
        a = encode_5421_bcd("99999999")
        b = encode_5421_bcd("1")
        r, ov = add_5421_bcd(a, b)
        self.assertTrue(ov)
        self.assertEqual(decode_5421_bcd(r), "0")
        a2 = encode_5421_bcd("1234")
        b2 = encode_5421_bcd("66")
        r2, ov2 = add_5421_bcd(a2, b2)
        self.assertFalse(ov2)
        self.assertEqual(decode_5421_bcd(r2), "1300")
