from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .bits import (
    bits_to_int_unsigned,
    compare_bits_unsigned,
    int_to_bits_unsigned,
)
from .int_codes import int_to_sign_magnitude, sign_magnitude_to_int, MAG_BITS, WIDTH, twos_subtract


@dataclass(frozen=True)
class SignMagResult:
    bits: List[int]
    decimal: int
    overflow: bool


def _mul_unsigned_bits(a: List[int], b: List[int], width: int) -> Tuple[List[int], bool]:
    """Shift-add multiplication, keep lower `width` bits, return overflow flag."""
    # a, b are msb-first
    if len(a) != width or len(b) != width:
        raise ValueError("width mismatch")

    a_lsb = list(reversed(a))
    b_lsb = list(reversed(b))
    acc = [0] * (2 * width)

    for i in range(width):
        if b_lsb[i] == 1:
            carry = 0
            for j in range(width):
                idx = i + j
                s = acc[idx] + a_lsb[j] + carry
                acc[idx] = s & 1
                carry = s >> 1
            k = i + width
            while carry and k < len(acc):
                s = acc[k] + carry
                acc[k] = s & 1
                carry = s >> 1
                k += 1

    overflow = any(acc[width:])
    low = list(reversed(acc[:width]))
    return low, overflow


def signmag_multiply(a_dec: int, b_dec: int) -> SignMagResult:
    """Multiply two signed integers represented in sign-magnitude form."""
    a_bits = int_to_sign_magnitude(a_dec)
    b_bits = int_to_sign_magnitude(b_dec)
    sign = a_bits[0] ^ b_bits[0]
    mag_a = a_bits[1:]
    mag_b = b_bits[1:]

    prod_mag, overflow = _mul_unsigned_bits(mag_a, mag_b, MAG_BITS)
    res_bits = [sign] + prod_mag
    res_dec = sign_magnitude_to_int(res_bits)
    return SignMagResult(bits=res_bits, decimal=res_dec, overflow=overflow)


@dataclass(frozen=True)
class SignMagFixed5Result:
    bits: List[int]
    scaled_decimal: int
    as_float_str: str
    overflow: bool
    div_by_zero: bool
    binary_str: str = ""
    int_quotient_bits: List[int] = None
    frac_quotient_bits: List[int] = None


FRAC_BITS = 17


def _div_long(a_mag: List[int], b_mag: List[int], num_bits: int) -> Tuple[List[int], List[int]]:
    w = len(b_mag)
    remainder = [0] * w
    quotient: List[int] = []

    for i in range(num_bits):
        remainder = remainder[1:] + [a_mag[i] if i < len(a_mag) else 0]

        if compare_bits_unsigned(remainder, b_mag) >= 0:
            quotient.append(1)
            remainder = twos_subtract(remainder, b_mag)
        else:
            quotient.append(0)

    return quotient, remainder


def signmag_divide_fixed5(a_dec: int, b_dec: int) -> SignMagFixed5Result:
    if b_dec == 0:
        return SignMagFixed5Result(
            bits=[0] * WIDTH,
            scaled_decimal=0,
            as_float_str="NaN",
            overflow=False,
            div_by_zero=True,
        )

    a_bits = int_to_sign_magnitude(a_dec)
    b_bits = int_to_sign_magnitude(b_dec)

    sign = a_bits[0] ^ b_bits[0]
    a_mag = a_bits[1:]
    b_mag = b_bits[1:]

    int_quotient, remainder = _div_long(a_mag, b_mag, MAG_BITS)

    # Fractional part: floor((remainder / divisor) * 2^FRAC_BITS)
    rem_int = bits_to_int_unsigned(remainder)
    div_int = bits_to_int_unsigned(b_mag)
    frac_q_int = (rem_int << FRAC_BITS) // div_int
    frac_quotient = int_to_bits_unsigned(frac_q_int, FRAC_BITS)

    int_q = bits_to_int_unsigned(int_quotient)
    overflow = int_q >= (1 << MAG_BITS)

    int_q_wrapped = int_q % (1 << MAG_BITS)
    mag_bits = int_to_bits_unsigned(int_q_wrapped, MAG_BITS)
    bits = [sign] + mag_bits

    int_str = "".join(str(b) for b in int_quotient).lstrip("0") or "0"
    frac_str = "".join(str(b) for b in frac_quotient)

    frac_val = bits_to_int_unsigned(frac_quotient)
    dec5 = (frac_val * 100000 + (1 << FRAC_BITS) // 2) // (1 << FRAC_BITS)
    dec5_str = str(dec5).zfill(5)[:5]

    as_str = ("-" if sign else "") + int_str + "." + dec5_str
    bin_str = ("-" if sign else "") + int_str + "." + frac_str

    scaled_q = int_q * 100000 + dec5
    scaled_signed = -scaled_q if sign else scaled_q

    return SignMagFixed5Result(
        bits=bits,
        scaled_decimal=scaled_signed,
        as_float_str=as_str,
        overflow=overflow,
        div_by_zero=False,
        binary_str=bin_str,
        int_quotient_bits=int_quotient,
        frac_quotient_bits=frac_quotient,
    )
