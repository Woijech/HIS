from __future__ import annotations

import os
import sys
from typing import List

if __package__ in (None, ""):
    # Allow running as a plain script: `python src/bitarith/__main__.py`.
    src_root = os.path.dirname(os.path.dirname(__file__))
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    from bitarith.int_codes import (
        int_to_sign_magnitude,
        int_to_ones_complement,
        int_to_twos_complement,
        sign_magnitude_to_int,
        ones_complement_to_int,
        twos_complement_to_int,
        twos_add,
        twos_subtract,
    )
    from bitarith.sign_magnitude_ops import signmag_multiply, signmag_divide_fixed5
    from bitarith.ieee754 import (
        decimal_str_to_ieee754,
        ieee754_to_decimal_str,
        ieee_add,
        ieee_sub,
        ieee_mul,
        ieee_div,
    )
    from bitarith.bcd5421 import encode_5421_bcd, decode_5421_bcd, add_5421_bcd
else:
    from .int_codes import (
        int_to_sign_magnitude,
        int_to_ones_complement,
        int_to_twos_complement,
        sign_magnitude_to_int,
        ones_complement_to_int,
        twos_complement_to_int,
        twos_add,
        twos_subtract,
    )
    from .sign_magnitude_ops import signmag_multiply, signmag_divide_fixed5
    from .ieee754 import (
        decimal_str_to_ieee754,
        ieee754_to_decimal_str,
        ieee_add,
        ieee_sub,
        ieee_mul,
        ieee_div,
    )
    from .bcd5421 import encode_5421_bcd, decode_5421_bcd, add_5421_bcd


def bits_to_str(bits: List[int]) -> str:
    return "".join("1" if b else "0" for b in bits)


def _read_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("Введите целое число в 10-ом формате (например: -13)")


def _read_dec_str(prompt: str) -> str:
    # Для IEEE: разрешаем +/-, точку, ведущие/хвостовые нули.
    while True:
        s = input(prompt).strip()
        if s and any(ch.isdigit() for ch in s):
            return s
        print("Введите десятичное число строкой (например: -3.25)")


def _read_digits(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s.isdigit() and len(s) <= 8:
            return s
        print("Введите не более 8 десятичных цифр (0..9), без знака")


def _print_intcodes(n: int) -> None:
    sm = int_to_sign_magnitude(n)
    oc = int_to_ones_complement(n)
    tc = int_to_twos_complement(n)
    print("\nDEC:", n)
    print("Прямой код (sign-magnitude):     ", bits_to_str(sm), "=>", sign_magnitude_to_int(sm))
    print("Обратный код (ones' complement): ", bits_to_str(oc), "=>", ones_complement_to_int(oc))
    print("Доп. код (two's complement):     ", bits_to_str(tc), "=>", twos_complement_to_int(tc))


def main() -> None:
    print("BitArith (32-bit, массивы 0/1). Выход: 0")
    while True:
        print(
            "\nМеню:\n"
            "  1) Перевод целого в двоичный (прямой/обратный/доп. коды)\n"
            "  2) Сложение 2 чисел в доп. коде (ввод в 10-ом)\n"
            "  3) Вычитание: A + (-B) в доп. коде (ввод в 10-ом)\n"
            "  4) Умножение 2 чисел в прямом коде (ввод в 10-ом)\n"
            "  5) Деление 2 чисел в прямом коде (ввод в 10-ом), точность 5 знаков\n"
            "  6) IEEE-754-2008 (32 bit): + - * / для чисел с плавающей точкой\n"
            "  7) Сложение 2 чисел в BCD 5421 (до 8 цифр)\n"
            "  0) Выход\n"
        )

        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            print("Пока!")
            return

        if choice == "1":
            n = _read_int("Введите целое (10): ")
            _print_intcodes(n)
            continue

        if choice == "2":
            a = _read_int("A (10): ")
            b = _read_int("B (10): ")
            aa = int_to_twos_complement(a)
            bb = int_to_twos_complement(b)
            rr = twos_add(aa, bb)
            print("\nA bits:", bits_to_str(aa), "dec:", twos_complement_to_int(aa))
            print("B bits:", bits_to_str(bb), "dec:", twos_complement_to_int(bb))
            print("SUM bits:", bits_to_str(rr), "dec:", twos_complement_to_int(rr))
            continue

        if choice == "3":
            a = _read_int("A (10): ")
            b = _read_int("B (10): ")
            aa = int_to_twos_complement(a)
            bb = int_to_twos_complement(b)
            rr = twos_subtract(aa, bb)
            print("\nA bits:", bits_to_str(aa), "dec:", twos_complement_to_int(aa))
            print("B bits:", bits_to_str(bb), "dec:", twos_complement_to_int(bb))
            print("RES bits:", bits_to_str(rr), "dec:", twos_complement_to_int(rr))
            continue

        if choice == "4":
            a = _read_int("A (10): ")
            b = _read_int("B (10): ")
            res = signmag_multiply(a, b)
            print("\nA (прямой):", bits_to_str(int_to_sign_magnitude(a)), "dec:", a)
            print("B (прямой):", bits_to_str(int_to_sign_magnitude(b)), "dec:", b)
            print("RES bits:", bits_to_str(res.bits), "dec:", res.decimal, "overflow=", res.overflow)
            continue

        if choice == "5":
            a = _read_int("A (10): ")
            b = _read_int("B (10): ")
            res = signmag_divide_fixed5(a, b)
            print("\nA (прямой):", bits_to_str(int_to_sign_magnitude(a)), "dec:", a)
            print("B (прямой):", bits_to_str(int_to_sign_magnitude(b)), "dec:", b)
            print("RES bits (целая часть):", bits_to_str(res.bits))
            if not res.div_by_zero:
                print("RES bin (с дробной частью):", res.binary_str)
            print("RES dec (точность 5):", res.as_float_str, "div0=", res.div_by_zero, "overflow=", res.overflow)
            continue

        if choice == "6":
            op = input("Операция (+, -, *, /): ").strip()
            if op not in {"+", "-", "*", "/"}:
                print("Неверная операция")
                continue
            x = _read_dec_str("X (10, строка): ")
            y = _read_dec_str("Y (10, строка): ")
            xb = decimal_str_to_ieee754(x)
            yb = decimal_str_to_ieee754(y)
            if op == "+":
                rb = ieee_add(xb, yb)
            elif op == "-":
                rb = ieee_sub(xb, yb)
            elif op == "*":
                rb = ieee_mul(xb, yb)
            else:
                rb = ieee_div(xb, yb)
            print("\nX bits:", bits_to_str(xb), "dec:", ieee754_to_decimal_str(xb))
            print("Y bits:", bits_to_str(yb), "dec:", ieee754_to_decimal_str(yb))
            print("R bits:", bits_to_str(rb), "dec:", ieee754_to_decimal_str(rb))
            continue

        if choice == "7":
            x = _read_digits("X (до 8 цифр): ")
            y = _read_digits("Y (до 8 цифр): ")
            xb = encode_5421_bcd(x)
            yb = encode_5421_bcd(y)
            rb, ov = add_5421_bcd(xb, yb)
            print("\nX bits:", bits_to_str(xb), "dec:", decode_5421_bcd(xb))
            print("Y bits:", bits_to_str(yb), "dec:", decode_5421_bcd(yb))
            print("R bits:", bits_to_str(rb), "dec:", decode_5421_bcd(rb), "overflow=", ov)
            continue

        print("Неизвестный пункт меню")


if __name__ == "__main__":
    main()
