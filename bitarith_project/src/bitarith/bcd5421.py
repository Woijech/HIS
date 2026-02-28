from __future__ import annotations

from typing import Dict, List, Tuple

WIDTH = 32
NIBBLES = 8
NIBBLE_BITS = 4

# 5421 weights correspond to bits [b3,b2,b1,b0] => [5,4,2,1]
# Encode digits by choosing the natural weight decomposition.
DIGIT_TO_NIBBLE: Dict[int, List[int]] = {
    0: [0, 0, 0, 0],
    1: [0, 0, 0, 1],
    2: [0, 0, 1, 0],
    3: [0, 0, 1, 1],
    4: [0, 1, 0, 0],
    5: [1, 0, 0, 0],
    6: [1, 0, 0, 1],
    7: [1, 0, 1, 0],
    8: [1, 0, 1, 1],
    9: [1, 1, 0, 0],
}

NIBBLE_TO_DIGIT: Dict[Tuple[int, int, int, int], int] = {tuple(v): k for k, v in DIGIT_TO_NIBBLE.items()}


def _normalize_decimal_str(s: str) -> str:
    if not s:
        raise ValueError("empty string")
    if any(ch < "0" or ch > "9" for ch in s):
        raise ValueError("BCD input must be digits only")
    # remove leading zeros but keep at least one digit
    i = 0
    while i + 1 < len(s) and s[i] == "0":
        i += 1
    return s[i:]


def encode_5421_bcd(decimal_digits: str) -> List[int]:
    """Encode up to 8 decimal digits into 32 bits (8 nibbles), left padded with zeros."""
    s = _normalize_decimal_str(decimal_digits)
    if len(s) > NIBBLES:
        raise ValueError("max 8 digits for 32-bit BCD 5421")
    s = "0" * (NIBBLES - len(s)) + s
    bits: List[int] = []
    for ch in s:
        d = ord(ch) - ord("0")
        bits.extend(DIGIT_TO_NIBBLE[d])
    return bits


def _decode_8_digits(bits32: List[int]) -> List[int]:
    if len(bits32) != WIDTH:
        raise ValueError("expected 32 bits")
    digits: List[int] = []
    for i in range(0, WIDTH, NIBBLE_BITS):
        nib = tuple(bits32[i : i + NIBBLE_BITS])
        d = NIBBLE_TO_DIGIT.get(nib)
        if d is None:
            raise ValueError("invalid 5421 nibble")
        digits.append(d)
    return digits


def decode_5421_bcd(bits32: List[int]) -> str:
    digits = _decode_8_digits(bits32)
    out_digits = [chr(ord("0") + d) for d in digits]
    # strip leading zeros
    s = "".join(out_digits)
    return _normalize_decimal_str(s)


def add_5421_bcd(a_bits: List[int], b_bits: List[int]) -> Tuple[List[int], bool]:
    """Add two 32-bit 5421-BCD numbers (8 digits). Returns (sum_bits32, overflow)."""
    a_digits = _decode_8_digits(a_bits)
    b_digits = _decode_8_digits(b_bits)

    carry = 0
    res_digits = [0] * NIBBLES
    for i in range(NIBBLES - 1, -1, -1):
        total = a_digits[i] + b_digits[i] + carry
        if total >= 10:
            total -= 10
            carry = 1
        else:
            carry = 0
        res_digits[i] = total

    overflow = carry != 0
    res_str = "".join(chr(ord("0") + d) for d in res_digits)
    return encode_5421_bcd(res_str), overflow
