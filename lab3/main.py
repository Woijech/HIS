"""CLI entry point for printing the generated circuit equations."""

from __future__ import annotations

from collections.abc import Iterable

from boolean_models import BooleanEquation
from circuit_equations import (
    build_bcd_adder_equations,
    build_bcd_decoder_equations,
    build_default_shifted_bcd_encoder_equations,
    build_down_counter_equations,
    build_subtractor_equations,
)
from circuit_specs import DEFAULT_ENCODER_OFFSET


def _print_equations(
    section_title: str,
    equation_list: Iterable[BooleanEquation],
    include_sdnf: bool = False,
) -> None:
    """Print a human-readable block of equations."""

    print(section_title)
    for equation in equation_list:
        if include_sdnf:
            print(
                f"{equation.label}:\n"
                f"SDNF: {equation.canonical_sop}\n"
                f"Minimized: {equation.minimized_expression}\n"
            )
        else:
            print(f"{equation.label} = {equation.minimized_expression}")
    print()


def main() -> None:
    """Generate and print all task equations."""

    _print_equations("ОДВ-3", build_subtractor_equations(), True)
    _print_equations("8421 BCD -> Двоичный", build_bcd_decoder_equations())
    _print_equations("Сумматор 8421 + 8421 -> двоичная сумма", build_bcd_adder_equations())
    _print_equations(
        f"Двоичный -> 8421 BCD (смещение n={DEFAULT_ENCODER_OFFSET}, десятки/единицы)",
        build_default_shifted_bcd_encoder_equations(),
    )
    _print_equations(
        "Двоичный счетчик вычитающего типа на 16 внутренних состояний в базисе НЕ-И ИЛИ и Т-триггер.",
        build_down_counter_equations(),
    )


if __name__ == "__main__":
    main()
