from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..domain.analysis import analyze_expression
from ..domain.models import AnalysisResult
from ..presentation.report_formatter import (
    render_calculation_minimization,
    render_canonical_forms,
    render_derivatives,
    render_fictive_variables,
    render_index_form,
    render_karnaugh_map,
    render_numeric_forms,
    render_overview,
    render_post_classes,
    render_report,
    render_table_minimization,
    render_truth_table,
    render_zhegalkin_polynomial,
)


HELP_TEXT = (
    'Справка по вводу:\n'
    '- допустимые переменные: a, b, c, d, e;\n'
    '- допустимые операции: !, &, |, ->, ~;\n'
    '- можно использовать скобки;\n'
    '- поддерживаются Unicode-символы: ¬, ∧, ∨, →, ↔, ≡;\n'
    '- пример: !(!a->!b)|c\n'
    '- пример: !(a&b) | (c -> a)\n'
)


Renderer = Callable[[AnalysisResult], str]


@dataclass(frozen=True)
class Operation:
    code: str
    title: str
    renderer: Renderer


OPERATIONS: tuple[Operation, ...] = (
    Operation('1', 'Таблица истинности', render_truth_table),
    Operation('2', 'СДНФ и СКНФ', render_canonical_forms),
    Operation('3', 'Числовая форма СДНФ и СКНФ', render_numeric_forms),
    Operation('4', 'Индексная форма', render_index_form),
    Operation('5', 'Классы Поста', render_post_classes),
    Operation('6', 'Полином Жегалкина', render_zhegalkin_polynomial),
    Operation('7', 'Фиктивные переменные', render_fictive_variables),
    Operation('8', 'Булева дифференциация', render_derivatives),
    Operation('9', 'Минимизация расчетным методом', render_calculation_minimization),
    Operation('10', 'Минимизация расчетно-табличным методом', render_table_minimization),
    Operation('11', 'Минимизация табличным методом', render_karnaugh_map),
    Operation('12', 'Краткая сводка', render_overview),
    Operation('13', 'Полный отчет', render_report),
)

_OPERATIONS_BY_CODE = {operation.code: operation for operation in OPERATIONS}


class AnalysisController:
    def __init__(self) -> None:
        self._result: AnalysisResult | None = None

    @property
    def current_expression(self) -> str | None:
        return None if self._result is None else self._result.expression

    def has_result(self) -> bool:
        return self._result is not None

    def set_expression(self, expression: str) -> AnalysisResult:
        self._result = analyze_expression(expression)
        return self._result

    def render_operation(self, code: str) -> tuple[str, str]:
        if self._result is None:
            raise ValueError('Сначала введите логическую функцию.')
        operation = _OPERATIONS_BY_CODE.get(code)
        if operation is None:
            raise ValueError('Неизвестная операция.')
        return operation.title, operation.renderer(self._result)
