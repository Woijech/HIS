from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


ValueT = TypeVar('ValueT')


@dataclass(frozen=True, slots=True)
class HashTableEntry(Generic[ValueT]):
    key: str
    value: ValueT
    numeric_value: int
    hash_address: int


@dataclass(frozen=True, slots=True)
class KeyDiagnostics:
    key: str
    numeric_value: int
    hash_address: int
    bucket_index: int


@dataclass(frozen=True, slots=True)
class BucketSnapshot(Generic[ValueT]):
    bucket_index: int
    hash_address: int
    size: int
    height: int
    root_key: str | None
    entries: tuple[HashTableEntry[ValueT], ...]


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
