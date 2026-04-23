"""Quine-McCluskey helpers with clearer public naming."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Final

from boolean_models import ImplicantTerm

NULL_IMPLICANT: Final[ImplicantTerm] = ImplicantTerm(0, 0)


def merge_if_single_bit_delta(
    first: ImplicantTerm, second: ImplicantTerm
) -> tuple[bool, ImplicantTerm]:
    """Merge two implicants when they differ in exactly one non-masked bit."""

    if first.mask != second.mask:
        return False, NULL_IMPLICANT

    delta = first.value ^ second.value
    if _has_single_active_bit(delta):
        merged = ImplicantTerm(
            bit_pattern=first.value & ~delta,
            wildcard_mask=first.mask | delta,
        )
        return True, merged

    return False, NULL_IMPLICANT


def render_full_disjunctive_form(
    variable_count: int,
    minterms: Iterable[int],
    variable_names: Sequence[str],
) -> str:
    """Build the canonical SDNF string for the provided minterms."""

    minterm_list = list(minterms)
    if not minterm_list:
        return "0"

    rendered_terms = [
        _render_implicant(ImplicantTerm(minterm, 0), variable_count, variable_names)
        for minterm in minterm_list
    ]
    return " | ".join(rendered_terms)


def minimize_disjunctive_form(
    variable_count: int,
    minterms: Iterable[int],
    dont_cares: Iterable[int] | None,
    variable_names: Sequence[str],
) -> str:
    """Return a minimized boolean expression for the given truth table."""

    minterm_list = list(minterms)
    if not minterm_list:
        return "0"

    dont_care_list = list(dont_cares or [])
    prime_implicants = _collect_prime_implicants(minterm_list, dont_care_list)
    essential_implicants, uncovered_minterms = _select_essential_implicants(
        prime_implicants,
        minterm_list,
    )
    final_cover = _complete_cover(uncovered_minterms, prime_implicants, essential_implicants)
    return _render_solution(final_cover, variable_count, variable_names)


def _has_single_active_bit(value: int) -> bool:
    """Return True when exactly one bit is set."""

    return value != 0 and (value & (value - 1)) == 0


def _collect_prime_implicants(
    minterms: list[int],
    dont_cares: list[int],
) -> list[ImplicantTerm]:
    """Generate all prime implicants for the truth table."""

    current_terms = _seed_implicant_terms(minterms, dont_cares)
    prime_terms: dict[ImplicantTerm, None] = {}

    while current_terms:
        next_terms: dict[ImplicantTerm, None] = {}
        merged_terms: set[ImplicantTerm] = set()

        for left_index, left_term in enumerate(current_terms):
            for right_index in range(left_index + 1, len(current_terms)):
                right_term = current_terms[right_index]
                can_merge, merged_term = merge_if_single_bit_delta(left_term, right_term)
                if can_merge:
                    next_terms[merged_term] = None
                    merged_terms.add(left_term)
                    merged_terms.add(right_term)

        for term in current_terms:
            if term not in merged_terms:
                prime_terms[term] = None

        current_terms = list(next_terms.keys())

    return list(prime_terms.keys())


def _seed_implicant_terms(minterms: list[int], dont_cares: list[int]) -> list[ImplicantTerm]:
    """Create the initial implicant list and remove duplicates."""

    terms = [ImplicantTerm(term, 0) for term in [*minterms, *dont_cares]]
    return list(dict.fromkeys(terms))


def _select_essential_implicants(
    prime_implicants: list[ImplicantTerm],
    minterms: list[int],
) -> tuple[list[ImplicantTerm], list[int]]:
    """Split implicants into essential ones and minterms left uncovered."""

    essential_implicants: list[ImplicantTerm] = []
    covered_minterms: set[int] = set()

    for minterm in minterms:
        covering_implicants = _find_covering_implicants(prime_implicants, minterm)
        if len(covering_implicants) == 1:
            essential_implicants = _append_if_missing(
                essential_implicants,
                covering_implicants[0],
            )

    for implicant in essential_implicants:
        for minterm in minterms:
            if implicant.covers(minterm):
                covered_minterms.add(minterm)

    uncovered_minterms = [
        minterm for minterm in minterms if minterm not in covered_minterms
    ]
    return essential_implicants, uncovered_minterms


def _find_covering_implicants(
    prime_implicants: list[ImplicantTerm],
    minterm: int,
) -> list[ImplicantTerm]:
    """Return prime implicants that cover the provided minterm."""

    return [implicant for implicant in prime_implicants if implicant.covers(minterm)]


def _append_if_missing(
    implicants: list[ImplicantTerm],
    candidate: ImplicantTerm,
) -> list[ImplicantTerm]:
    """Append an implicant when it is not already present."""

    if candidate in implicants:
        return implicants
    return [*implicants, candidate]


def _complete_cover(
    uncovered_minterms: list[int],
    prime_implicants: list[ImplicantTerm],
    essential_implicants: list[ImplicantTerm],
) -> list[ImplicantTerm]:
    """Greedily add implicants until all minterms are covered."""

    selected_implicants = list(essential_implicants)
    pending_minterms = list(uncovered_minterms)

    while pending_minterms:
        best_implicant = _choose_best_covering_implicant(prime_implicants, pending_minterms)
        selected_implicants.append(best_implicant)
        pending_minterms = [
            minterm for minterm in pending_minterms if not best_implicant.covers(minterm)
        ]

    return selected_implicants


def _choose_best_covering_implicant(
    prime_implicants: list[ImplicantTerm],
    uncovered_minterms: list[int],
) -> ImplicantTerm:
    """Choose the implicant that covers the most uncovered minterms."""

    best_coverage = -1
    best_implicant = prime_implicants[0]

    for implicant in prime_implicants:
        coverage = sum(1 for minterm in uncovered_minterms if implicant.covers(minterm))
        if coverage > best_coverage:
            best_coverage = coverage
            best_implicant = implicant

    return best_implicant


def _render_solution(
    implicants: list[ImplicantTerm],
    variable_count: int,
    variable_names: Sequence[str],
) -> str:
    """Render the final minimized expression."""

    rendered_terms: list[str] = []
    full_wildcard_mask = (1 << variable_count) - 1

    for implicant in implicants:
        if implicant.mask == full_wildcard_mask:
            return "1"
        rendered_terms.append(_render_implicant(implicant, variable_count, variable_names))

    return " | ".join(rendered_terms)


def _render_implicant(
    implicant: ImplicantTerm,
    variable_count: int,
    variable_names: Sequence[str],
) -> str:
    """Render a single implicant as a conjunction of literals."""

    literals: list[str] = []

    for variable_index in range(variable_count):
        bit_position = variable_count - 1 - variable_index
        if ((implicant.mask >> bit_position) & 1) == 0:
            if ((implicant.value >> bit_position) & 1) == 1:
                literals.append(variable_names[variable_index])
            else:
                literals.append("!" + variable_names[variable_index])

    return "(" + " & ".join(literals) + ")"
