"""Canonical builders for the logical equations used in the project."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from boolean_minimizer import minimize_disjunctive_form, render_full_disjunctive_form
from boolean_models import BooleanEquation
from circuit_specs import (
    ADDER_LAYOUT,
    BCD_CODE_SPACE,
    COUNTER_LAYOUT,
    COUNTER_STATE_COUNT,
    DECIMAL_BASE,
    DECODER_LAYOUT,
    DEFAULT_ENCODER_OFFSET,
    ENCODER_LAYOUT,
    ENCODER_TENS_OUTPUTS,
    ENCODER_UNITS_OUTPUTS,
    MAX_BCD_DIGIT,
    MAX_ENCODER_SOURCE_VALUE,
    SUBTRACTOR_LAYOUT,
)

MintermBuckets = dict[str, list[int]]


def _build_equation(
    label: str,
    input_names: Sequence[str],
    minterms: Iterable[int],
    dont_cares: Iterable[int] | None = None,
    *,
    include_canonical_sop: bool = False,
) -> BooleanEquation:
    """Create a boolean equation from active minterms and optional don't-cares."""

    input_name_list = list(input_names)
    minterm_list = list(minterms)
    dont_care_list = None if dont_cares is None else list(dont_cares)
    input_width = len(input_name_list)

    return BooleanEquation(
        label=label,
        canonical_sop=(
            render_full_disjunctive_form(input_width, minterm_list, input_name_list)
            if include_canonical_sop
            else ""
        ),
        minimized_expression=minimize_disjunctive_form(
            input_width,
            minterm_list,
            dont_care_list,
            input_name_list,
        ),
    )


def _create_output_buckets(output_names: Sequence[str]) -> MintermBuckets:
    """Create an empty minterm bucket for each output signal."""

    return {output_name: [] for output_name in output_names}


def _record_active_bits(
    output_buckets: MintermBuckets,
    output_names: Sequence[str],
    encoded_value: int,
    source_minterm: int,
) -> None:
    """Record which output bits are active for a source minterm."""

    bit_width = len(output_names)
    for bit_index, output_name in enumerate(output_names):
        bit_mask = 1 << (bit_width - bit_index - 1)
        if encoded_value & bit_mask:
            output_buckets[output_name].append(source_minterm)


def _compile_output_group(
    input_names: Sequence[str],
    output_names: Sequence[str],
    output_buckets: MintermBuckets,
    dont_cares: Iterable[int] | None = None,
) -> list[BooleanEquation]:
    """Compile a set of output buckets into minimized equations."""

    return [
        _build_equation(
            label=output_name,
            input_names=input_names,
            minterms=output_buckets[output_name],
            dont_cares=dont_cares,
        )
        for output_name in output_names
    ]


def _is_valid_bcd_digit(value: int) -> bool:
    """Return True when the value fits in one 8421 BCD digit."""

    return 0 <= value <= MAX_BCD_DIGIT


def decode_bcd_8421(value: int) -> tuple[int, bool]:
    """Decode a 4-bit 8421 BCD value into a decimal digit."""

    if _is_valid_bcd_digit(value):
        return value, True
    return -1, False


def encode_bcd_8421(value: int) -> int:
    """Encode a decimal digit into its 8421 BCD representation."""

    if _is_valid_bcd_digit(value):
        return value
    return 0


def build_subtractor_equations() -> list[BooleanEquation]:
    """Build equations for the one-bit full subtractor outputs."""

    return [
        _build_equation(
            label="d (Разность)",
            input_names=SUBTRACTOR_LAYOUT.input_names,
            minterms=(1, 2, 4, 7),
            include_canonical_sop=True,
        ),
        _build_equation(
            label="b (Заем)",
            input_names=SUBTRACTOR_LAYOUT.input_names,
            minterms=(1, 2, 3, 7),
            include_canonical_sop=True,
        ),
    ]


def build_bcd_decoder_equations() -> list[BooleanEquation]:
    """Build equations for the 8421 BCD to binary decoder."""

    output_buckets = _create_output_buckets(DECODER_LAYOUT.output_names)
    invalid_inputs: list[int] = []

    for input_value in range(BCD_CODE_SPACE):
        decoded_value, is_valid = decode_bcd_8421(input_value)
        if not is_valid:
            invalid_inputs.append(input_value)
            continue

        _record_active_bits(
            output_buckets=output_buckets,
            output_names=DECODER_LAYOUT.output_names,
            encoded_value=decoded_value,
            source_minterm=input_value,
        )

    return _compile_output_group(
        input_names=DECODER_LAYOUT.input_names,
        output_names=DECODER_LAYOUT.output_names,
        output_buckets=output_buckets,
        dont_cares=invalid_inputs,
    )


def build_bcd_adder_equations() -> list[BooleanEquation]:
    """Build equations for adding two valid 8421 BCD digits."""

    output_buckets = _create_output_buckets(ADDER_LAYOUT.output_names)
    invalid_inputs: list[int] = []

    for left_digit in range(BCD_CODE_SPACE):
        for right_digit in range(BCD_CODE_SPACE):
            combined_input = (left_digit << 4) | right_digit
            if not _is_valid_bcd_digit(left_digit) or not _is_valid_bcd_digit(right_digit):
                invalid_inputs.append(combined_input)
                continue

            _record_active_bits(
                output_buckets=output_buckets,
                output_names=ADDER_LAYOUT.output_names,
                encoded_value=left_digit + right_digit,
                source_minterm=combined_input,
            )

    return _compile_output_group(
        input_names=ADDER_LAYOUT.input_names,
        output_names=ADDER_LAYOUT.output_names,
        output_buckets=output_buckets,
        dont_cares=invalid_inputs,
    )


def build_shifted_bcd_encoder_equations(offset: int) -> list[BooleanEquation]:
    """Build equations for converting a shifted binary value into two BCD digits."""

    output_buckets = _create_output_buckets(ENCODER_LAYOUT.output_names)
    invalid_inputs = list(
        range(MAX_ENCODER_SOURCE_VALUE + 1, 1 << ENCODER_LAYOUT.input_width)
    )

    for input_value in range(MAX_ENCODER_SOURCE_VALUE + 1):
        tens_digit, units_digit = divmod(input_value + offset, DECIMAL_BASE)

        _record_active_bits(
            output_buckets=output_buckets,
            output_names=ENCODER_TENS_OUTPUTS,
            encoded_value=encode_bcd_8421(tens_digit),
            source_minterm=input_value,
        )
        _record_active_bits(
            output_buckets=output_buckets,
            output_names=ENCODER_UNITS_OUTPUTS,
            encoded_value=encode_bcd_8421(units_digit),
            source_minterm=input_value,
        )

    return _compile_output_group(
        input_names=ENCODER_LAYOUT.input_names,
        output_names=ENCODER_LAYOUT.output_names,
        output_buckets=output_buckets,
        dont_cares=invalid_inputs,
    )


def build_default_shifted_bcd_encoder_equations() -> list[BooleanEquation]:
    """Build encoder equations using the project-wide default offset."""

    return build_shifted_bcd_encoder_equations(DEFAULT_ENCODER_OFFSET)


def build_down_counter_equations() -> list[BooleanEquation]:
    """Build toggle equations for the 16-state down counter."""

    output_buckets = _create_output_buckets(COUNTER_LAYOUT.output_names)

    for current_state in range(COUNTER_STATE_COUNT):
        next_state = (current_state - 1) % COUNTER_STATE_COUNT
        toggled_bits = current_state ^ next_state

        _record_active_bits(
            output_buckets=output_buckets,
            output_names=COUNTER_LAYOUT.output_names,
            encoded_value=toggled_bits,
            source_minterm=current_state,
        )

    return _compile_output_group(
        input_names=COUNTER_LAYOUT.input_names,
        output_names=COUNTER_LAYOUT.output_names,
        output_buckets=output_buckets,
    )
