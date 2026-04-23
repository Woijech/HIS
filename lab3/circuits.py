"""Backward-compatible facade for the original circuit API."""

from __future__ import annotations

from boolean_models import BooleanEquation as Equation
from circuit_equations import (
    build_bcd_adder_equations,
    build_bcd_decoder_equations,
    build_default_shifted_bcd_encoder_equations,
    build_down_counter_equations,
    build_shifted_bcd_encoder_equations,
    build_subtractor_equations,
    decode_bcd_8421,
    encode_bcd_8421,
)


def get_subtractor_equations() -> list[Equation]:
    """Return equations for the one-bit full subtractor outputs."""

    return build_subtractor_equations()


def decode_8421(value: int) -> tuple[int, bool]:
    """Backward-compatible wrapper around the canonical 8421 decoder."""

    return decode_bcd_8421(value)


def encode_8421(value: int) -> int:
    """Backward-compatible wrapper around the canonical 8421 encoder."""

    return encode_bcd_8421(value)


def get_decoder_8421_equations() -> list[Equation]:
    """Return equations for the 8421 BCD decoder."""

    return build_bcd_decoder_equations()


def get_bcd_adder_equations() -> list[Equation]:
    """Return equations for the BCD adder."""

    return build_bcd_adder_equations()


def get_encoder_8421_equations(offset_n: int) -> list[Equation]:
    """Return equations for the shifted binary-to-BCD encoder."""

    return build_shifted_bcd_encoder_equations(offset_n)


def get_encoder_8421_equations_offset_n() -> list[Equation]:
    """Return encoder equations using the default project offset."""

    return build_default_shifted_bcd_encoder_equations()


def get_counter_equations() -> list[Equation]:
    """Return equations for the down counter toggle inputs."""

    return build_down_counter_equations()
