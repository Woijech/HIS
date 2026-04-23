from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .exceptions import InvalidKeyError


class KeyEncoder(Protocol):
    def to_numeric(self, key: str) -> int:
        """Transforms a textual key into its numeric value V."""


class AddressStrategy(Protocol):
    def to_address(self, numeric_value: int, capacity: int, base_address: int = 0) -> int:
        """Transforms a numeric key value into a hash address h(V)."""


RUSSIAN_ALPHABET: tuple[str, ...] = tuple('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')


@dataclass(frozen=True, slots=True)
class FirstLettersKeyEncoder:
    """Calculates V using the first N letters in a positional numeral system."""

    alphabet: tuple[str, ...] = RUSSIAN_ALPHABET
    letters_count: int = 2
    _letter_to_index: dict[str, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.letters_count <= 0:
            raise ValueError('Количество букв для кодирования должно быть положительным.')
        if not self.alphabet:
            raise ValueError('Алфавит не должен быть пустым.')
        object.__setattr__(
            self,
            '_letter_to_index',
            {letter: index for index, letter in enumerate(self.alphabet)},
        )

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


@dataclass(frozen=True, slots=True)
class ModuloHashAddressStrategy:
    """Implements h(V) = V mod H + B."""

    def to_address(self, numeric_value: int, capacity: int, base_address: int = 0) -> int:
        if capacity <= 0:
            raise ValueError('Размер таблицы должен быть положительным.')
        if base_address < 0:
            raise ValueError('Базовый адрес не может быть отрицательным.')
        return numeric_value % capacity + base_address
