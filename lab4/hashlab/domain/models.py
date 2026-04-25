from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HashTableEntry:
    key: str
    value: str
    numeric_value: int
    hash_address: int


@dataclass(frozen=True, slots=True)
class KeyDiagnostics:
    key: str
    numeric_value: int
    hash_address: int
    bucket_index: int


@dataclass(frozen=True, slots=True)
class BucketSnapshot:
    bucket_index: int
    hash_address: int
    size: int
    height: int
    root_key: str | None
    entries: tuple[HashTableEntry, ...]


@dataclass(frozen=True, slots=True)
class TableStatistics:
    capacity: int
    size: int
    used_buckets: int
    empty_buckets: int
    collision_buckets: int
    collisions: int
    max_chain_length: int
    max_tree_height: int
    load_factor: float
