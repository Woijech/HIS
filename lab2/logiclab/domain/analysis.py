from __future__ import annotations

from itertools import combinations, product
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .ast import Expr
from .karnaugh import build_karnaugh_map
from .minimization import (
    BitPattern,
    Implicant,
    bits_to_index,
    index_to_bits,
    minimize_minterms,
)
from .parser import parse_expression
from .models import AnalysisResult, Assignment, CanonicalForms, DerivativeInfo, PostClasses, TruthRow


def iter_assignments(variables: Sequence[str]) -> Iterable[Assignment]:
    yield from product((0, 1), repeat=len(variables))


def evaluate_expression(expr: Expr, variables: Sequence[str]) -> Tuple[TruthRow, ...]:
    rows: List[TruthRow] = []
    for bits in iter_assignments(variables):
        mapping = dict(zip(variables, bits))
        rows.append(TruthRow(values=tuple(bits), result=expr.evaluate(mapping)))
    return tuple(rows)


def _build_minterm(bits: Assignment, variables: Sequence[str]) -> str:
    if not variables:
        return '1'
    parts = [variable if bit == 1 else f'!{variable}' for variable, bit in zip(variables, bits)]
    return '(' + ' & '.join(parts) + ')'


def _build_maxterm(bits: Assignment, variables: Sequence[str]) -> str:
    if not variables:
        return '0'
    parts = [variable if bit == 0 else f'!{variable}' for variable, bit in zip(variables, bits)]
    return '(' + ' | '.join(parts) + ')'


def build_canonical_forms(rows: Sequence[TruthRow], variables: Sequence[str]) -> CanonicalForms:
    minterms = tuple(bits_to_index(row.values) for row in rows if row.result == 1)
    maxterms = tuple(bits_to_index(row.values) for row in rows if row.result == 0)

    sdnf_terms = [_build_minterm(row.values, variables) for row in rows if row.result == 1]
    sknf_terms = [_build_maxterm(row.values, variables) for row in rows if row.result == 0]

    sdnf = '0' if not sdnf_terms else ' | '.join(sdnf_terms)
    sknf = '1' if not sknf_terms else ' & '.join(sknf_terms)

    index_binary = ''.join(str(row.result) for row in rows)
    index_decimal = int(index_binary, 2) if index_binary else 0

    return CanonicalForms(
        sdnf=sdnf,
        sknf=sknf,
        sdnf_numeric=f'Σ{minterms}',
        sknf_numeric=f'Π{maxterms}',
        index_binary=index_binary,
        index_decimal=index_decimal,
        minterms=minterms,
        maxterms=maxterms,
    )


def _anf_coefficients(vector: Sequence[int]) -> List[int]:
    coeffs = list(vector)
    size = len(coeffs)
    step = 1
    while step < size:
        for mask in range(size):
            if mask & step:
                coeffs[mask] ^= coeffs[mask ^ step]
        step <<= 1
    return coeffs


def build_zhegalkin(variables: Sequence[str], rows: Sequence[TruthRow]) -> str:
    coeffs = _anf_coefficients([row.result for row in rows])
    terms: List[str] = []
    for index, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        if index == 0:
            terms.append('1')
            continue
        parts = [variables[pos] for pos in range(len(variables)) if (index >> (len(variables) - pos - 1)) & 1]
        terms.append(''.join(parts))
    return '0' if not terms else ' ⊕ '.join(terms)


def _is_self_dual(rows: Sequence[TruthRow]) -> bool:
    values = {row.values: row.result for row in rows}
    for bits, result in values.items():
        inverse = tuple(1 - bit for bit in bits)
        if result == values[inverse]:
            return False
    return True


def _is_monotone(rows: Sequence[TruthRow]) -> bool:
    values = {row.values: row.result for row in rows}
    keys = list(values)
    for left in keys:
        for right in keys:
            if all(a <= b for a, b in zip(left, right)) and values[left] > values[right]:
                return False
    return True


def _is_linear(rows: Sequence[TruthRow]) -> bool:
    coeffs = _anf_coefficients([row.result for row in rows])
    for index, coeff in enumerate(coeffs):
        if not coeff:
            continue
        if bin(index).count('1') > 1:
            return False
    return True


def build_post_classes(rows: Sequence[TruthRow]) -> PostClasses:
    first = rows[0].result
    last = rows[-1].result
    return PostClasses(
        t0=first == 0,
        t1=last == 1,
        s=_is_self_dual(rows),
        m=_is_monotone(rows),
        l=_is_linear(rows),
    )


def _derivative_truth_vector(expr: Expr, variables: Sequence[str], derivative_variables: Sequence[str]) -> Tuple[int, ...]:
    indexes = [variables.index(variable) for variable in derivative_variables]
    remaining_variables = tuple(variable for variable in variables if variable not in derivative_variables)
    remaining_indexes = [variables.index(variable) for variable in remaining_variables]
    vector: List[int] = []
    for remaining_bits in iter_assignments(remaining_variables):
        base = [0] * len(variables)
        for position, bit in zip(remaining_indexes, remaining_bits):
            base[position] = bit
        total = 0
        for toggle_size in range(2 ** len(indexes)):
            toggled = base[:]
            parity_bits = index_to_bits(toggle_size, len(indexes))
            for position, toggle_bit in zip(indexes, parity_bits):
                if toggle_bit:
                    toggled[position] ^= 1
            total ^= expr.evaluate(dict(zip(variables, toggled)))
        vector.append(total)
    return tuple(vector)


def build_derivatives(expr: Expr, variables: Sequence[str]) -> Tuple[DerivativeInfo, ...]:
    limit = min(4, len(variables))
    derivatives: List[DerivativeInfo] = []
    for size in range(1, limit + 1):
        for subset in combinations(variables, size):
            vector = _derivative_truth_vector(expr, variables, subset)
            remaining_variables = tuple(variable for variable in variables if variable not in subset)
            rows = tuple(
                TruthRow(values=bits, result=value)
                for bits, value in zip(iter_assignments(remaining_variables), vector)
            )
            canonical = build_canonical_forms(rows, remaining_variables)
            derivatives.append(
                DerivativeInfo(
                    variables=tuple(subset),
                    remaining_variables=remaining_variables,
                    truth_vector=vector,
                    index_binary=canonical.index_binary,
                    index_decimal=canonical.index_decimal,
                    sdnf=canonical.sdnf,
                )
            )
    return tuple(derivatives)


def _implicant_to_expression(pattern: BitPattern, variables: Sequence[str]) -> str:
    parts = []
    for variable, bit in zip(variables, pattern):
        if bit is None:
            continue
        parts.append(variable if bit == 1 else f'!{variable}')
    return '1' if not parts else (' & '.join(parts) if len(parts) == 1 else '(' + ' & '.join(parts) + ')')


def selected_implicants_to_dnf(implicants: Sequence[Implicant], variables: Sequence[str]) -> str:
    if not implicants:
        return '0'
    parts = [_implicant_to_expression(implicant.pattern, variables) for implicant in implicants]
    return ' | '.join(parts)


def _implicant_to_maxterm(pattern: BitPattern, variables: Sequence[str]) -> str:
    parts = []
    for variable, bit in zip(variables, pattern):
        if bit is None:
            continue
        parts.append(variable if bit == 0 else f'!{variable}')
    if not parts:
        return '0'
    if len(parts) == 1:
        return parts[0]
    return '(' + ' | '.join(parts) + ')'


def selected_implicants_to_cnf(implicants: Sequence[Implicant], variables: Sequence[str]) -> str:
    if not implicants:
        return '1'
    parts = [_implicant_to_maxterm(implicant.pattern, variables) for implicant in implicants]
    return ' & '.join(parts)


def _find_fictive_variables(expr: Expr, variables: Sequence[str]) -> Tuple[str, ...]:
    fictive = []
    for variable in variables:
        derivative_vector = _derivative_truth_vector(expr, variables, (variable,))
        if all(value == 0 for value in derivative_vector):
            fictive.append(variable)
    return tuple(fictive)


def analyze_expression(text: str) -> AnalysisResult:
    expr = parse_expression(text)
    variables = tuple(sorted(expr.variables()))
    if not variables:
        variables = tuple()
    if len(variables) > 5:
        raise ValueError('Допускается не более 5 переменных')

    rows = evaluate_expression(expr, variables)
    canonical = build_canonical_forms(rows, variables)
    post_classes = build_post_classes(rows)
    zhegalkin = build_zhegalkin(variables, rows)
    fictive_variables = _find_fictive_variables(expr, variables)
    derivatives = build_derivatives(expr, variables)
    minimization = minimize_minterms(canonical.minterms, len(variables))
    maxterm_minimization = minimize_minterms(canonical.maxterms, len(variables))
    truth_map = {row.values: row.result for row in rows}
    karnaugh = build_karnaugh_map(
        variables,
        truth_map,
        minimization.selected_implicants,
        maxterm_minimization.selected_implicants,
    )

    return AnalysisResult(
        expression=text,
        variables=variables,
        rows=rows,
        canonical=canonical,
        post_classes=post_classes,
        zhegalkin=zhegalkin,
        fictive_variables=fictive_variables,
        derivatives=derivatives,
        minimization=minimization,
        maxterm_minimization=maxterm_minimization,
        karnaugh=karnaugh,
    )
