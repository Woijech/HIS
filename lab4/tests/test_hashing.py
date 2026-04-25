import unittest

from hashlab.domain.exceptions import InvalidKeyError
from hashlab.domain.hashing import FirstLettersKeyEncoder, ModuloHashAddressStrategy


class TestHashing(unittest.TestCase):
    def setUp(self) -> None:
        self.encoder = FirstLettersKeyEncoder()
        self.strategy = ModuloHashAddressStrategy()

    def test_encoder_uses_first_two_letters(self) -> None:
        self.assertEqual(self.encoder.to_numeric('Вяткин'), 98)
        self.assertEqual(self.encoder.to_numeric('Третьяк'), 644)

    def test_hash_address_is_calculated_by_modulo(self) -> None:
        self.assertEqual(self.strategy.to_address(644, capacity=20), 4)
        self.assertEqual(self.strategy.to_address(98, capacity=20, base_address=100), 118)

    def test_encoder_rejects_short_or_empty_key(self) -> None:
        with self.assertRaises(InvalidKeyError):
            self.encoder.to_numeric('А')
        with self.assertRaises(InvalidKeyError):
            self.encoder.to_numeric('   ')

    def test_encoder_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            FirstLettersKeyEncoder(letters_count=0)
        with self.assertRaises(ValueError):
            FirstLettersKeyEncoder(alphabet=())

    def test_hash_address_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            self.strategy.to_address(10, capacity=0)
        with self.assertRaises(ValueError):
            self.strategy.to_address(10, capacity=5, base_address=-1)


if __name__ == '__main__':
    unittest.main()
