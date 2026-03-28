from __future__ import annotations

from typing import Iterable, List, Sequence

from ..domain.analysis import selected_implicants_to_dnf
from ..domain.minimization import BitPattern, GluingStage, Implicant
from ..domain.models import AnalysisResult


def _pattern_to_text(pattern: BitPattern, variables: Sequence[str]) -> str:
    parts = []
    for variable, bit in zip(variables, pattern):
        if bit is None:
            continue
        parts.append(variable if bit == 1 else f'!{variable}')
    if not parts:
        return '1'
    if len(parts) == 1:
        return parts[0]
    return '(' + ' & '.join(parts) + ')'


def _render_truth_table(result: AnalysisResult) -> str:
    header = ' | '.join((*result.variables, 'f'))
    separator = '-+-'.join('-' * max(1, len(item)) for item in (*result.variables, 'f'))
    rows = [' | '.join(map(str, (*row.values, row.result))) for row in result.rows]
    return '\n'.join([header, separator, *rows])


def _render_gluing_stage(stage: GluingStage, variables: Sequence[str], index: int) -> str:
    lines = [f'Этап склеивания {index}:']
    lines.append('  Исходные термы: ' + ', '.join(_pattern_to_text(pattern, variables) for pattern in stage.source_terms))
    if stage.combinations:
        lines.append('  Склеивания:')
        for record in stage.combinations:
            lines.append(
                f'    {_pattern_to_text(record.left, variables)} + '
                f'{_pattern_to_text(record.right, variables)} -> '
                f'{_pattern_to_text(record.result, variables)}'
            )
    lines.append('  Результат: ' + ', '.join(_pattern_to_text(pattern, variables) for pattern in stage.result_terms))
    return '\n'.join(lines)


def _render_prime_chart(result: AnalysisResult) -> str:
    primes = result.minimization.prime_implicants
    chart = result.minimization.chart
    if not primes:
        return 'Таблица простых импликант: функция тождественно равна 0.'
    header = ['Импликанта'] + [str(minterm) for minterm in result.canonical.minterms]
    widths = [max(len(item), 10) for item in header]
    lines = [' | '.join(item.ljust(width) for item, width in zip(header, widths))]
    lines.append('-+-'.join('-' * width for width in widths))
    selected = {implicant.pattern for implicant in result.minimization.selected_implicants}
    for idx, implicant in enumerate(primes):
        row = [_pattern_to_text(implicant.pattern, result.variables) + (' *' if implicant.pattern in selected else '')]
        for minterm in result.canonical.minterms:
            row.append('X' if chart[minterm][idx] else '')
        lines.append(' | '.join(item.ljust(width) for item, width in zip(row, widths)))
    return '\n'.join(lines)


def _render_karnaugh(result: AnalysisResult) -> str:
    lines: List[str] = ['Карта Карно:']
    for layer in result.karnaugh.layers:
        if layer.title:
            lines.append(layer.title)
        header = ['row\\col', *layer.column_labels]
        widths = [max(7, len(item)) for item in header]
        lines.append(' | '.join(item.ljust(width) for item, width in zip(header, widths)))
        lines.append('-+-'.join('-' * width for width in widths))
        for label, row in zip(layer.row_labels, layer.values):
            items = [label, *[str(value) for value in row]]
            lines.append(' | '.join(item.ljust(width) for item, width in zip(items, widths)))
        lines.append('')
    if result.karnaugh.groups:
        lines.append('Группы:')
        for group in result.karnaugh.groups:
            lines.append(f'  {group.term}: {", ".join(group.cells)}')
    return '\n'.join(lines).rstrip()


def render_overview(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            f'Исходное выражение: {result.expression}',
            f'Переменные: {", ".join(result.variables) if result.variables else "нет"}',
            f'Минимальная ДНФ: {selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables)}',
            (
                'Классы Поста: '
                + ' '.join(
                    f'{name}={"1" if value else "0"}'
                    for name, value in (
                        ('T0', result.post_classes.t0),
                        ('T1', result.post_classes.t1),
                        ('S', result.post_classes.s),
                        ('M', result.post_classes.m),
                        ('L', result.post_classes.l),
                    )
                )
            ),
            f'Полином Жегалкина: {result.zhegalkin}',
            f'Фиктивные переменные: {", ".join(result.fictive_variables) if result.fictive_variables else "нет"}',
        )
    )


def render_truth_table(result: AnalysisResult) -> str:
    return _render_truth_table(result)


def render_canonical_forms(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            f'СДНФ: {result.canonical.sdnf}',
            f'СКНФ: {result.canonical.sknf}',
        )
    )


def render_numeric_forms(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            f'Числовая форма СДНФ: {result.canonical.sdnf_numeric}',
            f'Числовая форма СКНФ: {result.canonical.sknf_numeric}',
        )
    )


def render_index_form(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            f'Индексная форма: {result.canonical.index_binary} = {result.canonical.index_decimal}',
        )
    )


def render_post_classes(result: AnalysisResult) -> str:
    return ' '.join(
        f'{name}={"1" if value else "0"}'
        for name, value in (
            ('T0', result.post_classes.t0),
            ('T1', result.post_classes.t1),
            ('S', result.post_classes.s),
            ('M', result.post_classes.m),
            ('L', result.post_classes.l),
        )
    )


def render_zhegalkin_polynomial(result: AnalysisResult) -> str:
    return f'Полином Жегалкина: {result.zhegalkin}'


def render_fictive_variables(result: AnalysisResult) -> str:
    return 'Фиктивные переменные: ' + (
        ', '.join(result.fictive_variables) if result.fictive_variables else 'нет'
    )


def render_post_analysis(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            'Классы Поста',
            render_post_classes(result),
            '',
            render_zhegalkin_polynomial(result),
            render_fictive_variables(result),
        )
    )


def render_derivatives(result: AnalysisResult) -> str:
    lines: List[str] = []
    for derivative in result.derivatives:
        lines.append(
            f"∂/∂{''.join(derivative.variables)}: "
            f'{derivative.index_binary} = {derivative.index_decimal}; '
            f'СДНФ: {derivative.sdnf}'
        )
    return '\n'.join(lines)


def render_calculation_minimization(result: AnalysisResult) -> str:
    lines: List[str] = []
    if result.minimization.stages:
        for index, stage in enumerate(result.minimization.stages, start=1):
            lines.append(_render_gluing_stage(stage, result.variables, index))
    else:
        lines.append('Склеивания нет.')
    lines.append('Простые импликанты: ' + (
        ', '.join(_pattern_to_text(item.pattern, result.variables) for item in result.minimization.prime_implicants)
        if result.minimization.prime_implicants
        else 'нет'
    ))
    lines.append('Минимальная ДНФ: ' + selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables))
    return '\n'.join(lines)


def render_table_minimization(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            _render_prime_chart(result),
            'Итог: ' + selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables),
        )
    )


def render_karnaugh_map(result: AnalysisResult) -> str:
    return '\n'.join(
        (
            _render_karnaugh(result),
            'Итог: ' + selected_implicants_to_dnf(result.minimization.selected_implicants, result.variables),
        )
    )


def render_report(result: AnalysisResult) -> str:
    overview_lines = render_overview(result).splitlines()
    lines: List[str] = []
    lines.append('Лабораторная работа №2')
    lines.append('Анализ логической функции')
    lines.append('=' * 72)
    lines.append(overview_lines[0])
    lines.append(overview_lines[1])
    lines.append('')
    lines.append('Таблица истинности')
    lines.append(render_truth_table(result))
    lines.append('')
    lines.append('Канонические формы')
    lines.append(render_canonical_forms(result))
    lines.append(render_numeric_forms(result))
    lines.append(render_index_form(result))
    lines.append('')
    lines.append(render_post_analysis(result))
    lines.append('')
    lines.append('Булевы производные')
    lines.append(render_derivatives(result))
    lines.append('')
    lines.append('Минимизация расчетным методом')
    lines.append(render_calculation_minimization(result))
    lines.append('')
    lines.append('Минимизация расчетно-табличным методом')
    lines.append(render_table_minimization(result))
    lines.append('')
    lines.append('Минимизация табличным методом')
    lines.append(render_karnaugh_map(result))
    return '\n'.join(lines)
