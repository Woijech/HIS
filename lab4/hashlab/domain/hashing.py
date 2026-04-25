from .exceptions import InvalidKeyError


RUSSIAN_ALPHABET: tuple[str, ...] = tuple('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')


class FirstLettersKeyEncoder:
    """Считает V(K) по первым буквам ключа."""

    def __init__(
        self,
        alphabet: tuple[str, ...] = RUSSIAN_ALPHABET,
        letters_count: int = 2,
    ) -> None:
        if letters_count <= 0:
            raise ValueError('Количество букв для кодирования должно быть положительным.')
        if not alphabet:
            raise ValueError('Алфавит не должен быть пустым.')

        self.alphabet = alphabet
        self.letters_count = letters_count
        self._letter_to_index = {letter: index for index, letter in enumerate(alphabet)}

    def to_numeric(self, key: str) -> int:
        normalized = self._normalize_letters(key)
        if len(normalized) < self.letters_count:
            raise InvalidKeyError(
                f"Ключ '{key}' должен содержать минимум {self.letters_count} букв "
                'из поддерживаемого алфавита.',
            )

        value = 0
        base = len(self.alphabet)
        for letter in normalized[: self.letters_count]:
            value = value * base + self._letter_to_index[letter]
        return value

    def _normalize_letters(self, key: str) -> list[str]:
        if not key or not key.strip():
            raise InvalidKeyError('Ключ не должен быть пустым.')
        return [letter for letter in key.upper() if letter in self._letter_to_index]


class ModuloHashAddressStrategy:
    """Считает адрес по формуле h(V) = V mod H + B."""

    def to_address(self, numeric_value: int, capacity: int, base_address: int = 0) -> int:
        if capacity <= 0:
            raise ValueError('Размер таблицы должен быть положительным.')
        if base_address < 0:
            raise ValueError('Базовый адрес не может быть отрицательным.')
        return numeric_value % capacity + base_address
