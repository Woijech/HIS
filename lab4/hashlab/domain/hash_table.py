from .avl_tree import AVLTree
from .exceptions import DuplicateKeyError, InvalidKeyError, KeyNotFoundError
from .hashing import FirstLettersKeyEncoder, ModuloHashAddressStrategy
from .models import BucketSnapshot, HashTableEntry, KeyDiagnostics, TableStatistics


class HashTable:
    def __init__(
        self,
        capacity: int,
        key_encoder: FirstLettersKeyEncoder | None = None,
        address_strategy: ModuloHashAddressStrategy | None = None,
        base_address: int = 0,
    ) -> None:
        if capacity <= 0:
            raise ValueError('Размер таблицы должен быть положительным.')
        if base_address < 0:
            raise ValueError('Базовый адрес не может быть отрицательным.')

        self._capacity = capacity
        self._base_address = base_address
        self._key_encoder = key_encoder or FirstLettersKeyEncoder()
        self._address_strategy = address_strategy or ModuloHashAddressStrategy()
        self._buckets = [AVLTree() for _ in range(capacity)]
        self._size = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def base_address(self) -> int:
        return self._base_address

    @property
    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        self._buckets = [AVLTree() for _ in range(self._capacity)]
        self._size = 0

    def inspect_key(self, key: str) -> KeyDiagnostics:
        normalized_key = self._normalize_key(key)
        numeric_value = self._key_encoder.to_numeric(normalized_key)
        hash_address = self._address_strategy.to_address(
            numeric_value,
            self._capacity,
            self._base_address,
        )
        bucket_index = hash_address - self._base_address
        if not 0 <= bucket_index < self._capacity:
            raise InvalidKeyError('Хеш-адрес вышел за пределы таблицы.')
        return KeyDiagnostics(
            key=normalized_key,
            numeric_value=numeric_value,
            hash_address=hash_address,
            bucket_index=bucket_index,
        )

    def bucket_size(self, bucket_index: int) -> int:
        self._ensure_bucket_index(bucket_index)
        return len(self._buckets[bucket_index])

    def insert(self, key: str, value: str) -> HashTableEntry:
        diagnostics = self.inspect_key(key)
        lookup_key = self._lookup_key(diagnostics.key)
        bucket = self._buckets[diagnostics.bucket_index]
        if bucket.contains(lookup_key):
            raise DuplicateKeyError(f"Ключ '{diagnostics.key}' уже существует в таблице.")

        entry = HashTableEntry(
            key=diagnostics.key,
            value=value,
            numeric_value=diagnostics.numeric_value,
            hash_address=diagnostics.hash_address,
        )
        bucket.insert(lookup_key, entry)
        self._size += 1
        return entry

    def get(self, key: str) -> HashTableEntry:
        diagnostics = self.inspect_key(key)
        bucket = self._buckets[diagnostics.bucket_index]
        try:
            return bucket.get(self._lookup_key(diagnostics.key))
        except KeyNotFoundError as error:
            raise KeyNotFoundError(f"Ключ '{diagnostics.key}' не найден в таблице.") from error

    def update(self, key: str, value: str) -> HashTableEntry:
        diagnostics = self.inspect_key(key)
        lookup_key = self._lookup_key(diagnostics.key)
        bucket = self._buckets[diagnostics.bucket_index]
        try:
            current = bucket.get(lookup_key)
        except KeyNotFoundError as error:
            raise KeyNotFoundError(f"Ключ '{diagnostics.key}' не найден в таблице.") from error

        updated = HashTableEntry(
            key=current.key,
            value=value,
            numeric_value=current.numeric_value,
            hash_address=current.hash_address,
        )
        bucket.replace(lookup_key, updated)
        return updated

    def delete(self, key: str) -> HashTableEntry:
        diagnostics = self.inspect_key(key)
        bucket = self._buckets[diagnostics.bucket_index]
        try:
            removed = bucket.delete(self._lookup_key(diagnostics.key))
        except KeyNotFoundError as error:
            raise KeyNotFoundError(f"Ключ '{diagnostics.key}' не найден в таблице.") from error
        self._size -= 1
        return removed

    def contains(self, key: str) -> bool:
        try:
            diagnostics = self.inspect_key(key)
        except InvalidKeyError:
            return False
        bucket = self._buckets[diagnostics.bucket_index]
        return bucket.contains(self._lookup_key(diagnostics.key))

    def bucket_snapshot(self, bucket_index: int) -> BucketSnapshot:
        self._ensure_bucket_index(bucket_index)
        bucket = self._buckets[bucket_index]
        root = bucket.root_value
        return BucketSnapshot(
            bucket_index=bucket_index,
            hash_address=self._base_address + bucket_index,
            size=len(bucket),
            height=bucket.height,
            root_key=None if root is None else root.key,
            entries=bucket.values(),
        )

    def snapshot(self) -> tuple[BucketSnapshot, ...]:
        return tuple(self.bucket_snapshot(index) for index in range(self._capacity))

    def statistics(self) -> TableStatistics:
        bucket_sizes = [len(bucket) for bucket in self._buckets]
        used_buckets = sum(1 for size in bucket_sizes if size > 0)
        collision_buckets = sum(1 for size in bucket_sizes if size > 1)
        collisions = sum(size - 1 for size in bucket_sizes if size > 1)
        max_chain_length = max(bucket_sizes, default=0)
        max_tree_height = max((bucket.height for bucket in self._buckets), default=0)
        return TableStatistics(
            capacity=self._capacity,
            size=self._size,
            used_buckets=used_buckets,
            empty_buckets=self._capacity - used_buckets,
            collision_buckets=collision_buckets,
            collisions=collisions,
            max_chain_length=max_chain_length,
            max_tree_height=max_tree_height,
            load_factor=self._size / self._capacity,
        )

    def _ensure_bucket_index(self, bucket_index: int) -> None:
        if not 0 <= bucket_index < self._capacity:
            raise IndexError('Индекс корзины вне диапазона таблицы.')

    @staticmethod
    def _normalize_key(key: str) -> str:
        if key is None:
            raise InvalidKeyError('Ключ не должен быть пустым.')
        normalized = ' '.join(key.split())
        if not normalized:
            raise InvalidKeyError('Ключ не должен быть пустым.')
        return normalized

    @staticmethod
    def _lookup_key(key: str) -> str:
        return key.casefold()
