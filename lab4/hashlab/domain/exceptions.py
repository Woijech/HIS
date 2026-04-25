class HashTableError(Exception):
    """Базовая ошибка хеш-таблицы."""


class InvalidKeyError(HashTableError):
    """Ключ нельзя обработать хеш-функцией."""


class DuplicateKeyError(HashTableError):
    """Запись с таким ключом уже есть в таблице."""


class KeyNotFoundError(HashTableError):
    """Запись с таким ключом не найдена."""
