from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .minimization import BitPattern, Implicant, bits_to_index


GRAY_1 = [(0,), (1,)]
GRAY_2 = [(0, 0), (0, 1), (1, 1), (1, 0)]


@dataclass(frozen=True)
class KarnaughLayer:
    title: str
    row_labels: Tuple[str, ...]
    column_labels: Tuple[str, ...]
    values: Tuple[Tuple[int, ...], ...]


@dataclass(frozen=True)
class KarnaughGroup:
    term: str
    cells: Tuple[str, ...]


@dataclass(frozen=True)
class KarnaughMap:
    layers: Tuple[KarnaughLayer, ...]
    groups: Tuple[KarnaughGroup, ...]


def _pattern_to_term(pattern: BitPattern, variables: Sequence[str]) -> str:
    parts = []
    for variable, bit in zip(variables, pattern):
        if bit is None:
            continue
        parts.append(variable if bit == 1 else f'!{variable}')
    return '1' if not parts else ' & '.join(parts)


def _contains(pattern: BitPattern, bits: Sequence[int]) -> bool:
    return all(mask is None or mask == bit for mask, bit in zip(pattern, bits))


def build_karnaugh_map(
    variables: Sequence[str],
    truth_map: Dict[Tuple[int, ...], int],
    selected_implicants: Sequence[Implicant],
) -> KarnaughMap:
    variables = tuple(variables)
    size = len(variables)
    if not 0 <= size <= 5:
        raise ValueError('Карта Карно поддерживает от 0 до 5 переменных')

    if size == 0:
        return KarnaughMap(
            layers=(
                KarnaughLayer(
                    title='',
                    row_labels=('∅',),
                    column_labels=('∅',),
                    values=((truth_map[tuple()],),),
                ),
            ),
            groups=tuple(
                KarnaughGroup(term=_pattern_to_term(implicant.pattern, variables), cells=('∅',))
                for implicant in selected_implicants
            ),
        )

    if size == 1:
        row_vars: Tuple[str, ...] = tuple()
        col_vars = (variables[0],)
        row_codes = [tuple()]
        col_codes = GRAY_1
        layer_codes = [tuple()]
        layer_titles = ['']
    elif size == 2:
        row_vars = (variables[0],)
        col_vars = (variables[1],)
        row_codes = GRAY_1
        col_codes = GRAY_1
        layer_codes = [tuple()]
        layer_titles = ['']
    elif size == 3:
        row_vars = (variables[0],)
        col_vars = (variables[1], variables[2])
        row_codes = GRAY_1
        col_codes = GRAY_2
        layer_codes = [tuple()]
        layer_titles = ['']
    elif size == 4:
        row_vars = (variables[0], variables[1])
        col_vars = (variables[2], variables[3])
        row_codes = GRAY_2
        col_codes = GRAY_2
        layer_codes = [tuple()]
        layer_titles = ['']
    else:
        layer_var = variables[0]
        row_vars = (variables[1], variables[2])
        col_vars = (variables[3], variables[4])
        row_codes = GRAY_2
        col_codes = GRAY_2
        layer_codes = GRAY_1
        layer_titles = [f'{layer_var}=0', f'{layer_var}=1']

    layers: List[KarnaughLayer] = []
    row_labels = tuple(''.join(str(bit) for bit in code) or '∅' for code in row_codes)
    col_labels = tuple(''.join(str(bit) for bit in code) or '∅' for code in col_codes)

    for layer_title, layer_code in zip(layer_titles, layer_codes):
        rows: List[Tuple[int, ...]] = []
        for row_code in row_codes:
            row_values = []
            for col_code in col_codes:
                bits = tuple(layer_code + row_code + col_code)
                row_values.append(truth_map[bits])
            rows.append(tuple(row_values))
        layers.append(
            KarnaughLayer(
                title=layer_title,
                row_labels=row_labels,
                column_labels=col_labels,
                values=tuple(rows),
            )
        )

    groups: List[KarnaughGroup] = []
    for implicant in selected_implicants:
        cells: List[str] = []
        for bits, value in truth_map.items():
            if value == 1 and _contains(implicant.pattern, bits):
                cells.append(''.join(str(bit) for bit in bits))
        groups.append(KarnaughGroup(term=_pattern_to_term(implicant.pattern, variables), cells=tuple(sorted(cells))))

    return KarnaughMap(layers=tuple(layers), groups=tuple(groups))
