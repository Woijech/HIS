from __future__ import annotations

from typing import List, Tuple

from .bits import (
    add_bits,
    bitwise_not,
    bits_to_int_unsigned,
    compare_bits_unsigned,
    increment_bits,
    int_to_bits_unsigned,
)


WIDTH = 32
MAG_BITS = 31


def _clip_to_mag(n: int) -> int:
    """Clip magnitude to 31 bits by wrapping (keeps lower 31 bits)."""
    if n < 0:
        n = -n
    limit = 1 << MAG_BITS
    return n % limit


def int_to_sign_magnitude(n: int) -> List[int]:
    """Return 32-bit sign-magnitude representation."""
    sign = 1 if n < 0 else 0
    mag = _clip_to_mag(n)
    mag_bits = int_to_bits_unsigned(mag, MAG_BITS)
    return [sign] + mag_bits


def sign_magnitude_to_int(bits: List[int]) -> int:
    if len(bits) != WIDTH:
        raise ValueError("expected 32 bits")
    sign = bits[0]
    mag = bits_to_int_unsigned(bits[1:])
    if mag == 0:
        return 0  # ignore -0
    return -mag if sign == 1 else mag


def int_to_ones_complement(n: int) -> List[int]:
    """Return 32-bit ones' complement representation."""
    if n == 0:
        return [0] * WIDTH
    if n > 0:
        return int_to_sign_magnitude(n)  # positive matches sign-magnitude for 32 bits
    # negative: invert all bits of positive representation
    pos = int_to_sign_magnitude(-n)
    return bitwise_not(pos)


def ones_complement_to_int(bits: List[int]) -> int:
    if len(bits) != WIDTH:
        raise ValueError("expected 32 bits")
    if bits == [0] * WIDTH:
        return 0
    if bits == [1] * WIDTH:
        return 0  # -0
    sign = bits[0]
    if sign == 0:
        return sign_magnitude_to_int(bits)
    # negative: invert to get positive sign-magnitude
    pos = bitwise_not(bits)
    return -sign_magnitude_to_int(pos)


def int_to_twos_complement(n: int) -> List[int]:
    """Return 32-bit two's complement representation, wrapping modulo 2^32."""
    mod = 1 << WIDTH
    x = n % mod
    return int_to_bits_unsigned(x, WIDTH)


def twos_complement_to_int(bits: List[int]) -> int:
    if len(bits) != WIDTH:
        raise ValueError("expected 32 bits")
    unsigned = bits_to_int_unsigned(bits)
    sign = bits[0]
    if sign == 0:
        return unsigned
    # negative: value = unsigned - 2^32
    return unsigned - (1 << WIDTH)


def twos_add(a: List[int], b: List[int]) -> List[int]:
    """Add in 2's complement (wrap modulo 2^32)."""
    s, _carry = add_bits(a, b)
    return s


def twos_negate(bits: List[int]) -> List[int]:
    """Negation in 2's complement: ~x + 1."""
    inv = bitwise_not(bits)
    inc, _carry = increment_bits(inv)
    return inc


def twos_subtract(a: List[int], b: List[int]) -> List[int]:
    """Subtraction in 2's complement: a + (-b)."""
    return twos_add(a, twos_negate(b))


def twos_abs(bits: List[int]) -> Tuple[List[int], int]:
    """Return (abs(bits), sign) where sign is 1 if original was negative."""
    if bits[0] == 0:
        return bits[:], 0
    return twos_negate(bits), 1


def twos_compare(a: List[int], b: List[int]) -> int:
    """Compare 2's complement signed values."""
    sa, sb = a[0], b[0]
    if sa != sb:
        return -1 if sa > sb else 1
    # For equal signs in fixed-width two's complement, unsigned ordering
    # matches signed ordering.
    return compare_bits_unsigned(a, b)
