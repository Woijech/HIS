from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Set, Tuple


BitPattern = Tuple[int | None, ...]


@dataclass(frozen=True)
class Implicant:
    pattern: BitPattern
    covered: frozenset[int]

    @property
    def literal_count(self) -> int:
        return sum(bit is not None for bit in self.pattern)


@dataclass(frozen=True)
class CombinationRecord:
    left: BitPattern
    right: BitPattern
    result: BitPattern


@dataclass(frozen=True)
class GluingStage:
    source_terms: Tuple[BitPattern, ...]
    combinations: Tuple[CombinationRecord, ...]
    result_terms: Tuple[BitPattern, ...]


@dataclass(frozen=True)
class MinimizationResult:
    stages: Tuple[GluingStage, ...]
    prime_implicants: Tuple[Implicant, ...]
    selected_implicants: Tuple[Implicant, ...]
    chart: Dict[int, Tuple[bool, ...]]


def bits_to_index(bits: Sequence[int]) -> int:
    index = 0
    for bit in bits:
        index = (index << 1) | int(bit)
    return index


def index_to_bits(index: int, width: int) -> Tuple[int, ...]:
    return tuple((index >> shift) & 1 for shift in reversed(range(width)))


def combine_patterns(first: BitPattern, second: BitPattern) -> BitPattern | None:
    diff_index = -1
    for idx, (left, right) in enumerate(zip(first, second)):
        if left == right:
            continue
        if left is None or right is None:
            return None
        if diff_index != -1:
            return None
        diff_index = idx
    if diff_index == -1:
        return None
    combined = list(first)
    combined[diff_index] = None
    return tuple(combined)


def deduplicate_patterns(patterns: Iterable[BitPattern]) -> Tuple[BitPattern, ...]:
    return tuple(sorted(set(patterns), key=lambda item: tuple(2 if bit is None else bit for bit in item)))


def initial_implicants(minterms: Sequence[int], width: int) -> Tuple[Implicant, ...]:
    return tuple(
        Implicant(pattern=index_to_bits(index, width), covered=frozenset({index}))
        for index in sorted(minterms)
    )


def build_gluing_stages(initial: Sequence[Implicant]) -> Tuple[Tuple[GluingStage, ...], Tuple[Implicant, ...]]:
    current = list(initial)
    stages: List[GluingStage] = []
    primes: List[Implicant] = []

    while current:
        combined_flags = [False] * len(current)
        next_map: Dict[BitPattern, Set[int]] = {}
        combinations_records: List[CombinationRecord] = []

        for left_index in range(len(current)):
            for right_index in range(left_index + 1, len(current)):
                result = combine_patterns(current[left_index].pattern, current[right_index].pattern)
                if result is None:
                    continue
                combined_flags[left_index] = True
                combined_flags[right_index] = True
                next_map.setdefault(result, set()).update(current[left_index].covered | current[right_index].covered)
                combinations_records.append(
                    CombinationRecord(
                        left=current[left_index].pattern,
                        right=current[right_index].pattern,
                        result=result,
                    )
                )

        for implicant, was_combined in zip(current, combined_flags):
            if not was_combined:
                primes.append(implicant)

        next_implicants = [
            Implicant(pattern=pattern, covered=frozenset(sorted(covered)))
            for pattern, covered in sorted(next_map.items(), key=lambda item: tuple(2 if bit is None else bit for bit in item[0]))
        ]

        if combinations_records:
            stages.append(
                GluingStage(
                    source_terms=tuple(item.pattern for item in current),
                    combinations=tuple(combinations_records),
                    result_terms=tuple(item.pattern for item in next_implicants),
                )
            )
        current = next_implicants

    unique_primes: Dict[BitPattern, Set[int]] = {}
    for implicant in primes:
        unique_primes.setdefault(implicant.pattern, set()).update(implicant.covered)
    merged_primes = tuple(
        Implicant(pattern=pattern, covered=frozenset(sorted(covered)))
        for pattern, covered in sorted(unique_primes.items(), key=lambda item: tuple(2 if bit is None else bit for bit in item[0]))
    )
    return tuple(stages), merged_primes


def build_prime_chart(primes: Sequence[Implicant], minterms: Sequence[int]) -> Dict[int, Tuple[bool, ...]]:
    minterms = tuple(sorted(minterms))
    chart: Dict[int, Tuple[bool, ...]] = {}
    for minterm in minterms:
        chart[minterm] = tuple(minterm in implicant.covered for implicant in primes)
    return chart


def choose_minimal_cover(primes: Sequence[Implicant], minterms: Sequence[int]) -> Tuple[Implicant, ...]:
    required = set(minterms)
    if not required:
        return tuple()

    chart = build_prime_chart(primes, minterms)
    essential_indices: Set[int] = set()
    covered: Set[int] = set()

    for minterm, mask in chart.items():
        indexes = [idx for idx, value in enumerate(mask) if value]
        if len(indexes) == 1:
            essential_indices.add(indexes[0])

    for idx in essential_indices:
        covered.update(primes[idx].covered)

    uncovered = required - covered
    optional_indices = [idx for idx in range(len(primes)) if idx not in essential_indices]

    best_subset: Tuple[int, ...] | None = None
    best_key: Tuple[int, int, Tuple[str, ...]] | None = None

    if not uncovered:
        best_subset = tuple(sorted(essential_indices))
    else:
        for subset_size in range(len(optional_indices) + 1):
            for subset in combinations(optional_indices, subset_size):
                all_indices = tuple(sorted(set(subset) | essential_indices))
                total_covered: Set[int] = set()
                for idx in all_indices:
                    total_covered.update(primes[idx].covered)
                if not uncovered.issubset(total_covered):
                    continue
                lexical = tuple(str(primes[idx].pattern) for idx in all_indices)
                key = (
                    len(all_indices),
                    sum(primes[idx].literal_count for idx in all_indices),
                    lexical,
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best_subset = all_indices
            if best_subset is not None:
                break

    assert best_subset is not None
    return tuple(primes[idx] for idx in best_subset)


def minimize_minterms(minterms: Sequence[int], width: int) -> MinimizationResult:
    minterms = tuple(sorted(set(minterms)))
    if not minterms:
        return MinimizationResult(
            stages=tuple(),
            prime_implicants=tuple(),
            selected_implicants=tuple(),
            chart={},
        )
    initial = initial_implicants(minterms, width)
    stages, primes = build_gluing_stages(initial)
    selected = choose_minimal_cover(primes, minterms)
    chart = build_prime_chart(primes, minterms)
    return MinimizationResult(
        stages=stages,
        prime_implicants=primes,
        selected_implicants=selected,
        chart=chart,
    )
