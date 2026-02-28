from __future__ import annotations

from typing import Dict, List, Tuple

WIDTH = 32
NIBBLES = 8
NIBBLE_BITS = 4
WEIGHTS = (5, 4, 2, 1)

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
VALID_NIBBLE_INTS = {
    (bits[0] << 3) | (bits[1] << 2) | (bits[2] << 1) | bits[3]
    for bits in DIGIT_TO_NIBBLE.values()
}
VALUE_TO_NIBBLE_INT: Dict[int, int] = {
    WEIGHTS[0] * bits[0] + WEIGHTS[1] * bits[1] + WEIGHTS[2] * bits[2] + WEIGHTS[3] * bits[3]:
        (bits[0] << 3) | (bits[1] << 2) | (bits[2] << 1) | bits[3]
    for bits in DIGIT_TO_NIBBLE.values()
}

ADD_5421_TABLE: Dict[Tuple[int, int, int], Tuple[int, int]] = {}
for a_nib in VALID_NIBBLE_INTS:
    a_val = WEIGHTS[0] * ((a_nib >> 3) & 1) + WEIGHTS[1] * ((a_nib >> 2) & 1) + WEIGHTS[2] * ((a_nib >> 1) & 1) + WEIGHTS[3] * (a_nib & 1)
    for b_nib in VALID_NIBBLE_INTS:
        b_val = WEIGHTS[0] * ((b_nib >> 3) & 1) + WEIGHTS[1] * ((b_nib >> 2) & 1) + WEIGHTS[2] * ((b_nib >> 1) & 1) + WEIGHTS[3] * (b_nib & 1)
        for carry_in in (0, 1):
            total = a_val + b_val + carry_in
            carry_out = 1 if total >= 10 else 0
            digit_out = total - 10 if total >= 10 else total
            ADD_5421_TABLE[(a_nib, b_nib, carry_in)] = (VALUE_TO_NIBBLE_INT[digit_out], carry_out)


def _nibble_bits_to_int(bits4: List[int]) -> int:
    """Convert 4 separate bits [b3,b2,b1,b0] to a 0..15 integer."""
    if len(bits4) != NIBBLE_BITS:
        raise ValueError("expected 4 bits")
    return (bits4[0] << 3) | (bits4[1] << 2) | (bits4[2] << 1) | bits4[3]


def _int_to_nibble_bits(n: int) -> List[int]:
    """Convert 0..15 integer to 4 bits [b3,b2,b1,b0]."""
    return [(n >> 3) & 1, (n >> 2) & 1, (n >> 1) & 1, n & 1]


def _normalize_decimal_str(s: str) -> str:
    """Validate and strip leading zeros from a decimal string."""
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
    """Decode 32 bits into 8 decimal digits; validates each 5421 nibble."""
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
    """Decode 32-bit 5421 BCD into a normalized decimal string."""
    digits = _decode_8_digits(bits32)
    out_digits = [chr(ord("0") + d) for d in digits]
    # strip leading zeros
    s = "".join(out_digits)
    return _normalize_decimal_str(s)


def add_5421_bcd(a_bits: List[int], b_bits: List[int]) -> Tuple[List[int], bool]:
    """Add two 32-bit 5421-BCD numbers in 5421 code. Returns (sum_bits32, overflow)."""
    if len(a_bits) != WIDTH or len(b_bits) != WIDTH:
        raise ValueError("expected 32 bits")

    carry = 0
    res_bits = [0] * WIDTH
    for i in range(WIDTH - NIBBLE_BITS, -1, -NIBBLE_BITS):
        a_nib = _nibble_bits_to_int(a_bits[i : i + NIBBLE_BITS])
        b_nib = _nibble_bits_to_int(b_bits[i : i + NIBBLE_BITS])
        if a_nib not in VALID_NIBBLE_INTS or b_nib not in VALID_NIBBLE_INTS:
            raise ValueError("invalid 5421 nibble")
        res_nib, carry = ADD_5421_TABLE[(a_nib, b_nib, carry)]
        res_bits[i : i + NIBBLE_BITS] = _int_to_nibble_bits(res_nib)

    overflow = carry != 0
    return res_bits, overflow
