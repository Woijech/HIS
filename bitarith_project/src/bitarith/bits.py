from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


def _validate_bit(b: int) -> None:
    if b not in (0, 1):
        raise ValueError("bit must be 0 or 1")


def _validate_bits(bits: Iterable[int], width: int) -> List[int]:
    out = list(bits)
    if len(out) != width:
        raise ValueError(f"expected {width} bits, got {len(out)}")
    for b in out:
        _validate_bit(b)
    return out


def int_to_bits_unsigned(n: int, width: int) -> List[int]:
    """Convert non-negative int to msb-first bit list of given width."""
    if n < 0:
        raise ValueError("n must be non-negative")
    bits = [0] * width
    x = n
    for i in range(width - 1, -1, -1):
        bits[i] = x % 2
        x //= 2
    return bits


def bits_to_int_unsigned(bits: Iterable[int]) -> int:
    """Convert msb-first bit list to unsigned int."""
    out = 0
    for b in bits:
        _validate_bit(b)
        out = out * 2 + b
    return out


def bitwise_not(bits: List[int]) -> List[int]:
    return [1 - b for b in bits]


def bitwise_and(a: List[int], b: List[int]) -> List[int]:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    return [a[i] & b[i] for i in range(len(a))]


def bitwise_xor(a: List[int], b: List[int]) -> List[int]:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    return [a[i] ^ b[i] for i in range(len(a))]


def add_bits(a: List[int], b: List[int]) -> Tuple[List[int], int]:
    """Binary addition of two equal-length msb-first bit lists. Returns (sum_bits, carry_out)."""
    if len(a) != len(b):
        raise ValueError("length mismatch")
    n = len(a)
    res = [0] * n
    carry = 0
    for i in range(n - 1, -1, -1):
        s = a[i] + b[i] + carry
        res[i] = s & 1 # same as s % 2
        carry = s >> 1 # same as s // 2
    return res, carry


def increment_bits(bits: List[int]) -> Tuple[List[int], int]:
    """Add 1 to bit list. Returns (new_bits, carry_out)."""
    one = [0] * len(bits)
    one[-1] = 1
    return add_bits(bits, one)


def compare_bits_unsigned(a: List[int], b: List[int]) -> int:
    """Unsigned compare: returns -1,0,1."""
    if len(a) != len(b):
        raise ValueError("length mismatch")
    for i in range(len(a)):
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    return 0


def shift_left(bits: List[int], k: int) -> List[int]:
    if k < 0:
        raise ValueError("k must be >=0")
    n = len(bits)
    if k >= n:
        return [0] * n
    return bits[k:] + [0] * k


def shift_right(bits: List[int], k: int) -> List[int]:
    if k < 0:
        raise ValueError("k must be >=0")
    n = len(bits)
    if k >= n:
        return [0] * n
    return [0] * k + bits[: n - k]


def shift_right_with_sticky_int(x: int, shift: int) -> int:
    """Right shift with sticky bit OR'ed into LSB if any lost bits were 1."""
    if shift <= 0:
        return x
    if x == 0:
        return 0
    if shift >= x.bit_length() + 2:
        # everything lost -> sticky 1
        return 1
    mask = (1 << shift) - 1
    lost = x & mask
    x >>= shift
    if lost != 0:
        x |= 1
    return x


def rshift_round_nearest_even(x: int, shift: int) -> int:
    """Round x / 2^shift to nearest-even (x>=0)."""
    if shift <= 0:
        return x << (-shift)
    if x == 0:
        return 0
    low_mask = (1 << shift) - 1
    low = x & low_mask
    hi = x >> shift
    half = 1 << (shift - 1)
    if low < half:
        return hi
    if low > half:
        return hi + 1
    # exactly half: round to even
    return hi + (hi & 1)


@dataclass(frozen=True)
class Bits32:
    """Immutable 32-bit container (msb-first)."""

    bits: Tuple[int, ...]

    def __post_init__(self) -> None:
        _validate_bits(self.bits, 32)

    @staticmethod
    def from_list(bits: List[int]) -> "Bits32":
        return Bits32(tuple(_validate_bits(bits, 32)))

    @staticmethod
    def from_unsigned_int(n: int) -> "Bits32":
        return Bits32(tuple(int_to_bits_unsigned(n, 32)))

    def to_list(self) -> List[int]:
        return list(self.bits)

    def to_unsigned_int(self) -> int:
        return bits_to_int_unsigned(self.bits)

    def __str__(self) -> str:
        # For display only (no conversions used in logic)
        return "".join("1" if b else "0" for b in self.bits)
