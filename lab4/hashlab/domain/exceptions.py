class HashTableError(Exception):
    """Base exception for hash table domain errors."""


class InvalidKeyError(HashTableError):
    """Raised when a key cannot be processed by the hashing algorithm."""


class DuplicateKeyError(HashTableError):
    """Raised when an insert operation targets an existing key."""


class KeyNotFoundError(HashTableError):
    """Raised when the requested key is absent from the table."""
