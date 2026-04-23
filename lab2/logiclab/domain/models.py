from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .karnaugh import KarnaughMap
from .minimization import MinimizationResult


Assignment = Tuple[int, ...]


@dataclass(frozen=True)
class TruthRow:
    values: Assignment
    result: int


@dataclass(frozen=True)
class CanonicalForms:
    sdnf: str
    sknf: str
    sdnf_numeric: str
    sknf_numeric: str
    index_binary: str
    index_decimal: int
    minterms: Tuple[int, ...]
    maxterms: Tuple[int, ...]


@dataclass(frozen=True)
class PostClasses:
    t0: bool
    t1: bool
    s: bool
    m: bool
    l: bool


@dataclass(frozen=True)
class DerivativeInfo:
    variables: Tuple[str, ...]
    remaining_variables: Tuple[str, ...]
    truth_vector: Tuple[int, ...]
    index_binary: str
    index_decimal: int
    sdnf: str


@dataclass(frozen=True)
class AnalysisResult:
    expression: str
    variables: Tuple[str, ...]
    rows: Tuple[TruthRow, ...]
    canonical: CanonicalForms
    post_classes: PostClasses
    zhegalkin: str
    fictive_variables: Tuple[str, ...]
    derivatives: Tuple[DerivativeInfo, ...]
    minimization: MinimizationResult
    maxterm_minimization: MinimizationResult
    karnaugh: KarnaughMap
