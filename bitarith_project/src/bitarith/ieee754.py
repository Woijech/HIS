from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .bits import (
    bits_to_int_unsigned,
    int_to_bits_unsigned,
    rshift_round_nearest_even,
    shift_right_with_sticky_int,
)

WIDTH = 32
EXP_BITS = 8
FRAC_BITS = 23
BIAS = 127
MAX_EXP_FIELD = 255


@dataclass(frozen=True)
class IEEEUnpacked:
    """
    Unpacked IEEE-754 single-precision (float32) representation.

    Fields:
      - sign: 0 or 1
      - exp_field: 8-bit exponent field (0..255)
      - frac: 23-bit fraction field (0..2^23-1)

    Notes:
      - Normal values use an implicit leading 1, so significand = 1.frac
      - Subnormal values do not use the implicit leading 1, so significand = 0.frac
      - exp_field = 255 is used for Inf/NaN
      - exp_field = 0 is used for Zero/Subnormal
    """

    sign: int
    exp_field: int
    frac: int

    def is_nan(self) -> bool:
        """True if the value is NaN (exp_field=255 and frac!=0)."""
        return self.exp_field == 255 and self.frac != 0

    def is_inf(self) -> bool:
        """True if the value is ±Infinity (exp_field=255 and frac=0)."""
        return self.exp_field == 255 and self.frac == 0

    def is_zero(self) -> bool:
        """True if the value is ±0 (exp_field=0 and frac=0)."""
        return self.exp_field == 0 and self.frac == 0

    def is_subnormal(self) -> bool:
        """True if the value is subnormal (exp_field=0 and frac!=0)."""
        return self.exp_field == 0 and self.frac != 0

    def is_normal(self) -> bool:
        """True if the value is normal (0<exp_field<255)."""
        return 0 < self.exp_field < 255


def unpack_ieee754(bits32: List[int]) -> IEEEUnpacked:
    """
    Unpack 32 IEEE-754 single bits into an IEEEUnpacked structure.

    Input:
      - bits32: list of length 32, each element is 0 or 1
        bits32[0]  -> sign
        bits32[1:9] -> exp_field (8 bits)
        bits32[9:]  -> frac (23 bits)

    Output:
      - IEEEUnpacked(sign, exp_field, frac)

    Errors:
      - ValueError if the input length is not 32.
    """
    if len(bits32) != WIDTH:
        raise ValueError(f"expected {WIDTH} bits")
    if any(bit not in (0, 1) for bit in bits32):
        raise ValueError("bits must contain only 0/1")
    sign = bits32[0]
    exp_field = bits_to_int_unsigned(bits32[1: 1 + EXP_BITS])
    frac = bits_to_int_unsigned(bits32[1 + EXP_BITS :])
    return IEEEUnpacked(sign=sign, exp_field=exp_field, frac=frac)


def pack_ieee754(sign: int, exp_field: int, frac: int) -> List[int]:
    """
    Pack an IEEE-754 single from sign/exp_field/frac fields.

    Input:
      - sign: 0 or 1
      - exp_field: 0..255
      - frac: 0..(2^23-1)

    Output:
      - list of 32 bits.

    Errors:
      - ValueError for invalid ranges.
    """
    if sign not in (0, 1):
        raise ValueError("bad sign")
    if not (0 <= exp_field <= MAX_EXP_FIELD):
        raise ValueError("bad exp_field")
    if not (0 <= frac < (1 << FRAC_BITS)):
        raise ValueError("bad frac")
    bits = [sign]
    bits.extend(int_to_bits_unsigned(exp_field, EXP_BITS))
    bits.extend(int_to_bits_unsigned(frac, FRAC_BITS))
    return bits


def ieee754_to_rational(bits32: List[int]) -> Tuple[int, int, int]:
    """
    Convert IEEE-754 single (32 bits) to a binary-power rational representation.

    Returns a tuple (sign, numerator>=0, pow2_den>=0), where:
      value = (-1)^sign * numerator / 2^pow2_den

    Special values are encoded as:
      - Inf: (sign, 1, -1)
      - NaN: (sign, 0, -1)

    For finite values:
      - Zero: (sign, 0, 0)
      - Subnormal: value = frac * 2^-149 -> (sign, frac, 149)
      - Normal:
          value = (2^23 + frac) * 2^(exp_field - 127 - 23)
                = (2^23 + frac) * 2^(exp_field - 150)

        If exp2>=0, the numerator can be shifted and denominator set to 1.
    """
    u = unpack_ieee754(bits32)
    if u.is_nan():
        return u.sign, 0, -1
    if u.is_inf():
        return u.sign, 1, -1
    if u.is_zero():
        return u.sign, 0, 0
    if u.is_subnormal():
        return u.sign, u.frac, 149

    sig = (1 << 23) + u.frac
    exp2 = u.exp_field - 150
    if exp2 >= 0:
        return u.sign, sig << exp2, 0
    return u.sign, sig, -exp2


def ieee754_to_decimal_str(bits32: List[int], digits: int = 10) -> str:
    """
    Convert IEEE-754 single (32 bits) to a decimal string without using Python float.

    Method:
      1) Convert to rational form value = num / 2^k (via ieee754_to_rational).
      2) Generate fractional digits by long division: multiply remainder by 10 and take the integer part.

    Parameters:
      - digits: number of digits after the decimal point (fixed width).

    Returns:
      - "NaN", "Inf", "-Inf" for special values
      - "0.0" for zero
      - otherwise a string like "-12.3450000000" (trailing zeros are not trimmed).
    """
    sign, num, den_pow2 = ieee754_to_rational(bits32)
    if den_pow2 == -1:
        if num == 0:
            return "NaN"
        return "-Inf" if sign else "Inf"
    if num == 0:
        return "0.0"

    neg = sign == 1
    den = 1 << den_pow2
    whole = num // den
    rem = num % den
    out = "-" if neg else ""
    out += str(whole)
    out += "."
    for _ in range(digits):
        rem *= 10
        d = rem // den
        rem = rem % den
        out += chr(ord("0") + int(d))
    return out


def _parse_decimal_to_rational(s: str) -> Tuple[int, int, int]:
    """
    Parse a decimal string into a base-10 rational representation.

    Returns (sign, num>=0, scale10>=0), where:
      value = (-1)^sign * num / 10^scale10

    Supports:
      - leading/trailing spaces
      - '+'/'-' sign
      - decimal point '.'
      - exponent 'e'/'E' (for example "1.23e-4")

    Normalization:
      - leading zeros in the integer part are reduced
      - trailing zeros in the fractional part are removed (to reduce scale10)
      - exponent e:
          if e>0: num *= 10^e
          if e<0: scale10 += -e
    """
    if not s:
        raise ValueError("empty")
    s = s.strip()
    if not s:
        raise ValueError("empty")
    sign = 0
    if s[0] == "-":
        sign = 1
        s = s[1:]
    elif s[0] == "+":
        s = s[1:]
    if not s:
        raise ValueError("empty")

    exp10 = 0
    if "e" in s or "E" in s:
        parts = s.split("e") if "e" in s else s.split("E")
        if len(parts) != 2:
            raise ValueError("bad exponent")
        s, epart = parts[0], parts[1]
        if not epart:
            raise ValueError("bad exponent")
        esign = 1
        if epart[0] == "-":
            esign = -1
            epart = epart[1:]
        elif epart[0] == "+":
            epart = epart[1:]
        if not epart or any(ch < "0" or ch > "9" for ch in epart):
            raise ValueError("bad exponent digits")
        exp10 = 0
        for ch in epart:
            exp10 = exp10 * 10 + (ord(ch) - ord("0"))
        exp10 *= esign

    if "." in s:
        a, b = s.split(".", 1)
    else:
        a, b = s, ""
    if (not a and not b) or any((ch < "0" or ch > "9") for ch in (a + b)):
        raise ValueError("bad digits")

    if a:
        i = 0
        while i + 1 < len(a) and a[i] == "0":
            i += 1
        a = a[i:]

    while b and b[-1] == "0":
        b = b[:-1]

    scale10 = len(b)
    digits = (a if a else "0") + b
    num = 0
    for ch in digits:
        num = num * 10 + (ord(ch) - ord("0"))

    if exp10 > 0:
        num *= 10**exp10
    elif exp10 < 0:
        scale10 += (-exp10)

    return sign, num, scale10


def _cmp_scaled_pow2(num: int, den10_pow: int, e2: int) -> int:
    """
    Compare num/10^den10_pow with 2^e2.

    Returns:
      -1 if num/10^den10_pow < 2^e2
       0 if equal
       1 if greater

    The comparison is purely integer-based, without float:
      - for e2>=0 compare num ? (10^den10_pow)*2^e2
      - for e2<0 compare num*2^{-e2} ? 10^den10_pow
    """
    if e2 >= 0:
        rhs = (10**den10_pow) << e2
        if num < rhs:
            return -1
        if num > rhs:
            return 1
        return 0

    lhs = num << (-e2)
    rhs = 10**den10_pow
    if lhs < rhs:
        return -1
    if lhs > rhs:
        return 1
    return 0


def _find_binary_exponent(num: int, den10_pow: int) -> int:
    """
    Find e such that:
        2^e <= num/10^den10_pow < 2^(e+1)
    assuming num>0.

    Uses:
      - bit_length-based estimate (coarse log2)
      - then while-loop correction with exact comparisons via _cmp_scaled_pow2.

    This yields the normalization binary exponent needed for IEEE754.
    """
    den = 10**den10_pow
    e = (num.bit_length() - 1) - (den.bit_length() - 1)
    while _cmp_scaled_pow2(num, den10_pow, e) < 0:
        e -= 1
    while _cmp_scaled_pow2(num, den10_pow, e + 1) >= 0:
        e += 1
    return e


def decimal_str_to_ieee754(s: str) -> List[int]:
    """
    Convert a decimal string to IEEE-754 single (32 bits) without struct/float.

    High-level algorithm:
      1) Parse the string into rational num/10^scale10.
      2) If num==0 -> ±0.
      3) Find binary exponent e such that value is in [2^e, 2^(e+1)).
      4) Handle:
         - overflow -> Inf
         - subnormal -> compute frac as round(value / 2^-149)
         - normal -> build 23 mantissa bits via binary long division and rounding
      5) Rounding: round-to-nearest, ties-to-even (banker's rounding).

    Returns:
      - list of 32 bits.
    """
    sign, num, scale10 = _parse_decimal_to_rational(s)
    if num == 0:
        return pack_ieee754(sign, 0, 0)

    e = _find_binary_exponent(num, scale10)

    if e > 127:
        return pack_ieee754(sign, 255, 0)

    if e < -126:
        shift = 149
        den = 10**scale10
        numerator = num << shift
        q = numerator // den
        r = numerator % den
        twice_r = r * 2
        if twice_r > den:
            q += 1
        elif twice_r == den:
            if q & 1:
                q += 1
        if q >= (1 << 23):
            return pack_ieee754(sign, 1, 0)
        return pack_ieee754(sign, 0, int(q))

    den = 10**scale10
    if e >= 0:
        denom2 = den << e
        num2 = num
    else:
        denom2 = den
        num2 = num << (-e)

    rem = num2 - denom2
    mant = 0
    guard = 0
    rnd = 0
    for i in range(FRAC_BITS + 2):
        rem *= 2
        bit = rem // denom2
        rem = rem % denom2
        if i < FRAC_BITS:
            mant = (mant << 1) + int(bit)
        elif i == FRAC_BITS:
            guard = int(bit)
        else:
            rnd = int(bit)
    sticky = 1 if rem != 0 else 0

    if guard == 1:
        if rnd == 1 or sticky == 1 or (mant & 1) == 1:
            mant += 1
            if mant >= (1 << FRAC_BITS):
                mant = 0
                e += 1
                if e > 127:
                    return pack_ieee754(sign, 255, 0)

    exp_field = e + BIAS
    return pack_ieee754(sign, exp_field, mant)


def _pack_from_significand_exp2(sign: int, sig: int, exp2: int) -> List[int]:
    """
    Pack IEEE-754 single from an integer significand and a power of two:

        value = (-1)^sign * sig * 2^exp2

    Here sig>=0 is an integer (it may be wider than 24 bits).
    Goals:
      - normalize sig to 24-bit form (including hidden 1) for normal values
      - round correctly (round-to-nearest-even)
      - handle overflow (Inf)
      - handle subnormal (exp_field=0) with rounding to 23 bits

    Uses functions from .bits:
      - rshift_round_nearest_even: right shift with banker's rounding
    """
    if sig == 0:
        return pack_ieee754(sign, 0, 0)

    m = sig.bit_length() - 1
    shift = m - 23

    if shift > 0:
        sig24 = rshift_round_nearest_even(sig, shift)
        exp2n = exp2 + shift
    else:
        sig24 = sig << (-shift)
        exp2n = exp2 + shift

    if sig24 >= (1 << 24):
        sig24 >>= 1
        exp2n += 1

    exponent_unbiased = exp2n + 23
    if exponent_unbiased > 127:
        return pack_ieee754(sign, 255, 0)

    if exponent_unbiased >= -126:
        exp_field = exponent_unbiased + BIAS
        frac = sig24 & ((1 << 23) - 1)
        return pack_ieee754(sign, exp_field, frac)

    k = exp2 + 149
    if k >= 0:
        frac_full = sig << k
    else:
        frac_full = rshift_round_nearest_even(sig, -k)

    if frac_full == 0:
        return pack_ieee754(sign, 0, 0)

    if frac_full >= (1 << 23):
        return pack_ieee754(
            sign,
            1,
            int(frac_full - (1 << 23)) if frac_full < (1 << 24) else 0,
        )

    return pack_ieee754(sign, 0, int(frac_full))


def _unpack_to_sig_exp2(bits32: List[int]) -> Tuple[int, int, int, str]:
    """
    Unpack IEEE-754 single into the form:
      (sign, sig, exp2, kind)

    kind ∈ {'zero','sub','norm','inf','nan'}

    For finite values:
      value = (-1)^sign * sig * 2^exp2

    Rules:
      - zero: sig=0
      - subnormal: value = frac * 2^-149 => sig=frac, exp2=-149
      - normal: sig=(2^23 + frac), exp2=(exp_field - BIAS) - 23
      - inf/nan: sig/exp2 may be zeros; kind is what matters
    """
    u = unpack_ieee754(bits32)
    if u.is_nan():
        return u.sign, 0, 0, "nan"
    if u.is_inf():
        return u.sign, 0, 0, "inf"
    if u.is_zero():
        return u.sign, 0, 0, "zero"
    if u.is_subnormal():
        return u.sign, u.frac, -149, "sub"
    sig = (1 << 23) + u.frac
    exp2 = (u.exp_field - BIAS) - 23
    return u.sign, sig, exp2, "norm"


def ieee_add(a_bits: List[int], b_bits: List[int]) -> List[int]:
    """
    Add two IEEE-754 single values in bit form without using float.

    Approach:
      1) Unpack both inputs into (sign, sig, exp2, kind).
      2) Handle NaN/Inf.
      3) For non-zero finite values:
         - align exp2 exponents (shift significands)
         - add or subtract significands depending on signs
         - pack result via _pack_from_significand_exp2

    Precision:
      - alignment uses "extended" significands (<<3)
        to preserve guard/round/sticky bits during shifts.
      - shift_right_with_sticky_int from .bits provides sticky-bit handling
        when tail bits are lost.
    """
    sign_a, sig_a, exp2_a, kind_a = _unpack_to_sig_exp2(a_bits)
    sign_b, sig_b, exp2_b, kind_b = _unpack_to_sig_exp2(b_bits)

    if kind_a == "nan" or kind_b == "nan":
        return pack_ieee754(0, 255, 1)
    if kind_a == "inf":
        if kind_b == "inf" and sign_a != sign_b:
            return pack_ieee754(0, 255, 1)
        return pack_ieee754(sign_a, 255, 0)
    if kind_b == "inf":
        return pack_ieee754(sign_b, 255, 0)

    if sig_a == 0:
        return b_bits[:]
    if sig_b == 0:
        return a_bits[:]

    sig_a_ext = sig_a << 3
    sig_b_ext = sig_b << 3
    if exp2_a > exp2_b:
        diff = exp2_a - exp2_b
        sig_b_ext = shift_right_with_sticky_int(sig_b_ext, diff)
        aligned_exp2 = exp2_a
    elif exp2_b > exp2_a:
        diff = exp2_b - exp2_a
        sig_a_ext = shift_right_with_sticky_int(sig_a_ext, diff)
        aligned_exp2 = exp2_b
    else:
        aligned_exp2 = exp2_a

    if sign_a == sign_b:
        result_sig = sig_a_ext + sig_b_ext
        result_sign = sign_a
    else:
        if sig_a_ext >= sig_b_ext:
            result_sig = sig_a_ext - sig_b_ext
            result_sign = sign_a
        else:
            result_sig = sig_b_ext - sig_a_ext
            result_sign = sign_b

    return _pack_from_significand_exp2(result_sign, result_sig, aligned_exp2 - 3)


def ieee_sub(a_bits: List[int], b_bits: List[int]) -> List[int]:
    """
    Subtract a - b as a + (-b).
    This is done by flipping b's sign bit.
    """
    b = b_bits[:]
    b[0] = 1 - b[0]
    return ieee_add(a_bits, b)


def ieee_mul(a_bits: List[int], b_bits: List[int]) -> List[int]:
    """
    Multiply two IEEE-754 single values without float.

    Idea:
      - unpack into (sign, sig, exp2, kind)
      - handle NaN/Inf/0 according to IEEE-754 semantics
      - for finite values:
          sign = sign_a XOR sign_b
          sig = sig_a * sig_b
          exp2 = exp2_a + exp2_b
        then pack via _pack_from_significand_exp2

    To improve accuracy, a few extra low bits are added before packing (<<3),
    so rounding is more accurate.
    """
    sign_a, sig_a, exp2_a, kind_a = _unpack_to_sig_exp2(a_bits)
    sign_b, sig_b, exp2_b, kind_b = _unpack_to_sig_exp2(b_bits)

    if kind_a == "nan" or kind_b == "nan":
        return pack_ieee754(0, 255, 1)
    if (kind_a == "inf" and kind_b == "zero") or (kind_b == "inf" and kind_a == "zero"):
        return pack_ieee754(0, 255, 1)
    if kind_a == "inf" or kind_b == "inf":
        return pack_ieee754(sign_a ^ sign_b, 255, 0)
    if sig_a == 0 or sig_b == 0:
        return pack_ieee754(sign_a ^ sign_b, 0, 0)

    result_sign = sign_a ^ sign_b
    result_sig = sig_a * sig_b
    result_exp2 = exp2_a + exp2_b
    result_sig_ext = result_sig << 3
    return _pack_from_significand_exp2(result_sign, result_sig_ext, result_exp2 - 3)


def ieee_div(a_bits: List[int], b_bits: List[int]) -> List[int]:
    """
    Divide two IEEE-754 single values without float.

    Idea:
      - unpack into (sign, sig, exp2, kind)
      - handle NaN/Inf/0:
          inf/inf -> NaN
          inf/x -> inf
          x/inf -> 0
          x/0 -> inf (if x!=0), 0/0 -> NaN
      - for finite values:
          sign = sign_a XOR sign_b
          compute q = sig_a / sig_b with extra precision bits
          exp2 = exp2_a - exp2_b - extra
        then pack q*2^exp2 via _pack_from_significand_exp2

    Technique:
      - extra defines how many additional precision bits to keep in the numerator.
      - sticky effect for non-zero remainder is implemented by setting q's least significant bit.
    """
    sign_a, sig_a, exp2_a, kind_a = _unpack_to_sig_exp2(a_bits)
    sign_b, sig_b, exp2_b, kind_b = _unpack_to_sig_exp2(b_bits)

    if kind_a == "nan" or kind_b == "nan":
        return pack_ieee754(0, 255, 1)
    if kind_a == "inf" and kind_b == "inf":
        return pack_ieee754(0, 255, 1)
    if kind_a == "inf":
        return pack_ieee754(sign_a ^ sign_b, 255, 0)
    if kind_b == "inf":
        return pack_ieee754(sign_a ^ sign_b, 0, 0)
    if kind_b == "zero":
        if kind_a == "zero":
            return pack_ieee754(0, 255, 1)
        return pack_ieee754(sign_a ^ sign_b, 255, 0)
    if kind_a == "zero":
        return pack_ieee754(sign_a ^ sign_b, 0, 0)

    result_sign = sign_a ^ sign_b
    extra = 40
    numerator = sig_a << extra
    quotient = numerator // sig_b
    remainder = numerator % sig_b
    if remainder != 0:
        quotient |= 1
    result_exp2 = exp2_a - exp2_b - extra
    return _pack_from_significand_exp2(result_sign, quotient, result_exp2)
