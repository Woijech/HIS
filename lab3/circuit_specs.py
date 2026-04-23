"""Canonical circuit and number-system specifications used by the project."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SignalLayout:
    """Named input and output signals for a logic block."""

    input_names: tuple[str, ...]
    output_names: tuple[str, ...]

    @property
    def input_width(self) -> int:
        """Return the number of input signals."""

        return len(self.input_names)

    @property
    def output_width(self) -> int:
        """Return the number of output signals."""

        return len(self.output_names)


DECIMAL_BASE = 10
MAX_BCD_DIGIT = 9
BCD_CODE_SPACE = 16
MAX_ENCODER_SOURCE_VALUE = 18
DEFAULT_ENCODER_OFFSET = 4

SUBTRACTOR_LAYOUT = SignalLayout(("X1", "X2", "X3"), ("d", "b"))
DECODER_LAYOUT = SignalLayout(("I3", "I2", "I1", "I0"), ("O3", "O2", "O1", "O0"))
ADDER_LAYOUT = SignalLayout(
    ("A3", "A2", "A1", "A0", "B3", "B2", "B1", "B0"),
    ("S4", "S3", "S2", "S1", "S0"),
)
ENCODER_LAYOUT = SignalLayout(
    ("S4", "S3", "S2", "S1", "S0"),
    ("T3", "T2", "T1", "T0", "U3", "U2", "U1", "U0"),
)
COUNTER_LAYOUT = SignalLayout(("Q3", "Q2", "Q1", "Q0"), ("T3", "T2", "T1", "T0"))

ENCODER_TENS_OUTPUTS = ENCODER_LAYOUT.output_names[:4]
ENCODER_UNITS_OUTPUTS = ENCODER_LAYOUT.output_names[4:]

COUNTER_STATE_COUNT = 1 << COUNTER_LAYOUT.input_width
