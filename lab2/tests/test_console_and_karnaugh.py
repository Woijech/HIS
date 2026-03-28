from __future__ import annotations

import io
import unittest

from logiclab.application.menu_controller import AnalysisController
from logiclab.domain.analysis import analyze_expression
from logiclab.domain.karnaugh import build_karnaugh_map
from logiclab.presentation.console import run_console
from logiclab.presentation.report_formatter import render_report


class ConsoleAndKarnaughTests(unittest.TestCase):
    def run_console_session(self, *answers: str) -> tuple[int, str]:
        buffer = io.StringIO()
        answer_iter = iter(answers)

        def fake_input(_: str) -> str:
            return next(answer_iter)

        exit_code = run_console(input_func=fake_input, output=buffer)
        return exit_code, buffer.getvalue()

    def test_karnaugh_map_for_three_variables_has_expected_shape(self) -> None:
        result = analyze_expression('a|b|c')
        self.assertEqual(len(result.karnaugh.layers), 1)
        layer = result.karnaugh.layers[0]
        self.assertEqual(len(layer.values), 2)
        self.assertEqual(len(layer.values[0]), 4)

    def test_karnaugh_map_for_five_variables_has_two_layers(self) -> None:
        result = analyze_expression('a|b|c|d|e')
        self.assertEqual(len(result.karnaugh.layers), 2)

    def test_controller_returns_operation_content_for_current_function(self) -> None:
        controller = AnalysisController()
        controller.set_expression('a|b')
        title, content = controller.render_operation('1')
        self.assertEqual(title, 'Таблица истинности')
        self.assertIn('a | b | f', content)

    def test_console_can_show_full_report_for_current_function(self) -> None:
        exit_code, output = self.run_console_session('a|b', '13', '0')
        self.assertEqual(exit_code, 0)
        self.assertIn('Таблица истинности', output)
        self.assertIn('Минимизация табличным методом', output)
        self.assertIn('Завершение программы.', output)

    def test_operations_menu_runs_selected_operation(self) -> None:
        exit_code, output = self.run_console_session('a|b', '1', '0')
        self.assertEqual(exit_code, 0)
        self.assertIn('Операции над текущей функцией', output)
        self.assertIn('Таблица истинности', output)
        self.assertIn('a | b | f', output)

    def test_console_menu_handles_invalid_operation_choice(self) -> None:
        _, output = self.run_console_session('a|b', '77', '0')
        self.assertIn('Неизвестная операция.', output)

    def test_console_menu_shows_help(self) -> None:
        _, output = self.run_console_session('h', '0')
        self.assertIn('Справка по вводу', output)
        self.assertIn('!(!a->!b)|c', output)

    def test_console_menu_rejects_empty_expression(self) -> None:
        _, output = self.run_console_session('', '0')
        self.assertIn('Выражение не должно быть пустым.', output)

    def test_operations_menu_can_replace_current_function(self) -> None:
        _, output = self.run_console_session('a|b', 'n', 'a&b', '12', '0')
        self.assertIn('Исходное выражение: a&b', output)

    def test_expression_prompt_can_exit_immediately(self) -> None:
        exit_code, output = self.run_console_session('0')
        self.assertEqual(exit_code, 0)
        self.assertIn('Завершение программы.', output)

    def test_karnaugh_map_for_four_variables_has_4x4_grid(self) -> None:
        result = analyze_expression('(a&b)|(c&d)')
        layer = result.karnaugh.layers[0]
        self.assertEqual(len(layer.values), 4)
        self.assertEqual(len(layer.values[0]), 4)

    def test_render_report_handles_constant_zero(self) -> None:
        result = analyze_expression('0')
        report = render_report(result)
        self.assertIn('Склеивания нет.', report)
        self.assertIn('функция тождественно равна 0', report)

    def test_build_karnaugh_map_rejects_too_many_variables(self) -> None:
        with self.assertRaises(ValueError):
            build_karnaugh_map(('a', 'b', 'c', 'd', 'e', 'f'), {}, ())
