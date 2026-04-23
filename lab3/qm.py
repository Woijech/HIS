"""Backward-compatible facade over the canonical boolean minimizer."""

from boolean_minimizer import (
    NULL_IMPLICANT as EMPTY_IMPLICANT,
    _append_if_missing,
    _choose_best_covering_implicant,
    _collect_prime_implicants,
    _complete_cover,
    _find_covering_implicants,
    _render_implicant,
    _render_solution,
    _select_essential_implicants,
    merge_if_single_bit_delta,
    minimize_disjunctive_form,
    render_full_disjunctive_form,
)
from boolean_models import ImplicantTerm as Implicant


def differ_by_one_bit(first: Implicant, second: Implicant) -> tuple[bool, Implicant]:
    """Backward-compatible wrapper for the implicant merge helper."""

    return merge_if_single_bit_delta(first, second)


def generate_sdnf(variable_count: int, minterms, variable_names) -> str:
    """Backward-compatible wrapper for the canonical SDNF renderer."""

    return render_full_disjunctive_form(variable_count, minterms, variable_names)


def minimize(variable_count: int, minterms, dont_cares, variable_names) -> str:
    """Backward-compatible wrapper for the canonical minimizer."""

    return minimize_disjunctive_form(variable_count, minterms, dont_cares, variable_names)


_find_prime_implicants = _collect_prime_implicants
_find_essential_primes = _select_essential_implicants
_get_covers = _find_covering_implicants
_append_unique = _append_if_missing
_cover_remaining = _complete_cover
_find_best_prime = _choose_best_covering_implicant

__all__ = [
    "EMPTY_IMPLICANT",
    "Implicant",
    "_append_unique",
    "_cover_remaining",
    "_find_best_prime",
    "_find_essential_primes",
    "_find_prime_implicants",
    "_format_implicant",
    "_format_solution",
    "_get_covers",
    "differ_by_one_bit",
    "generate_sdnf",
    "minimize",
]

_format_implicant = _render_implicant
_format_solution = _render_solution
