from __future__ import annotations

import sys
from typing import Callable, TextIO

from ..application.menu_controller import AnalysisController, HELP_TEXT, OPERATIONS


InputFunc = Callable[[str], str]

APP_TITLE = ''
SEPARATOR = '=' * 72


def _println(output: TextIO, text: str = '') -> None:
    output.write(text + '\n')


def _print_section(output: TextIO, title: str, body: str) -> None:
    _println(output, SEPARATOR)
    _println(output, title)
    _println(output, SEPARATOR)
    _println(output, body.rstrip())


def _ask(input_func: InputFunc, output: TextIO, prompt: str) -> str:
    if input_func is input and output is sys.stdout:
        return input_func(prompt)
    output.write(prompt)
    return input_func('')


def _operations_menu(controller: AnalysisController) -> str:
    lines = [
        '',
        APP_TITLE,
        'Операции над текущей функцией',
        f'Функция: {controller.current_expression or "не выбрана"}',
        '',
    ]
    for operation in OPERATIONS:
        lines.append(f'{operation.code}. {operation.title}')
    lines.extend(
        (
            'n. Ввести новую функцию',
            'h. Справка по вводу',
            '0. Выход',
        )
    )
    return '\n'.join(lines) + '\n'


def _prompt_expression(
    controller: AnalysisController,
    input_func: InputFunc,
    output: TextIO,
) -> int:
    _println(output, APP_TITLE)
    _println(output, 'Введите логическую функцию для анализа.')
    _println(output, "Для выхода введите '0', для справки введите 'h'.")

    while True:
        expression = _ask(input_func, output, 'Введите логическое выражение: ').strip()
        if expression == '0':
            _println(output, 'Завершение программы.')
            return 0
        if expression.lower() == 'h':
            _print_section(output, 'Справка по вводу', HELP_TEXT)
            continue

        if not expression:
            _println(output, 'Выражение не должно быть пустым.')
            continue

        try:
            controller.set_expression(expression)
        except Exception as error:  # noqa: BLE001 - controlled message for console UI
            _println(output, f'Ошибка: {error}')
            continue
        return 1


def _run_operations_menu(
    controller: AnalysisController,
    input_func: InputFunc,
    output: TextIO,
) -> int:
    if not controller.has_result():
        return _prompt_expression(controller, input_func, output)

    while True:
        _println(output, _operations_menu(controller).rstrip())
        choice = _ask(input_func, output, 'Выберите операцию: ').strip().lower()

        if choice == '0':
            _println(output, 'Завершение программы.')
            return 0

        if choice == 'n':
            if _prompt_expression(controller, input_func, output) == 0:
                return 0
            continue

        if choice == 'h':
            _print_section(output, 'Справка по вводу', HELP_TEXT)
            continue

        try:
            title, content = controller.render_operation(choice)
        except ValueError as error:
            _println(output, str(error))
            continue
        _print_section(output, title, content)


def run_console(input_func: InputFunc = input, output: TextIO | None = None) -> int:
    stream = output if output is not None else sys.stdout
    controller = AnalysisController()
    if _prompt_expression(controller, input_func, stream) == 0:
        return 0
    return _run_operations_menu(controller, input_func, stream)


def main(
    argv: list[str] | None = None,
    input_func: InputFunc = input,
    output: TextIO | None = None,
) -> int:
    _ = argv
    return run_console(input_func=input_func, output=output)


if __name__ == '__main__':
    raise SystemExit(main())
