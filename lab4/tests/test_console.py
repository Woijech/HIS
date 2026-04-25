from io import StringIO
import sys
import unittest
from unittest.mock import patch

from hashlab.presentation.console import _ask, main
from hashlab.presentation.formatter import render_table


class TestConsole(unittest.TestCase):
    def test_console_can_load_demo_and_show_stats(self) -> None:
        answers = iter(['7', '6', '0'])
        output = StringIO()

        exit_code = main(argv=[], input_func=lambda _: next(answers), output=output)
        rendered = output.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn('Демонстрационные данные', rendered)
        self.assertIn('Количество коллизий', rendered)
        self.assertIn('Завершение программы.', rendered)

    def test_console_crud_help_clear_and_unknown_command(self) -> None:
        answers = iter([
            '1', 'Алгоритм', 'Первое описание',
            '2', 'алгоритм',
            '3', 'алгоритм', 'Новое описание',
            '5',
            '4', 'алгоритм',
            '8',
            '9',
            'x',
            '2', 'Нет',
            '0',
        ])
        output = StringIO()

        exit_code = main(argv=[], input_func=lambda _: next(answers), output=output)
        rendered = output.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn('Добавление записи', rendered)
        self.assertIn('Коллизия при вставке: нет', rendered)
        self.assertIn('Запись найдена', rendered)
        self.assertIn('Запись обновлена', rendered)
        self.assertIn('Новое описание', rendered)
        self.assertIn('Содержимое таблицы', rendered)
        self.assertIn('Запись удалена', rendered)
        self.assertIn('Таблица очищена.', rendered)
        self.assertIn('Формула из методички', rendered)
        self.assertIn('Неизвестная команда.', rendered)
        self.assertIn('Ошибка:', rendered)

    def test_console_loads_demo_from_argument(self) -> None:
        output = StringIO()

        exit_code = main(argv=['--demo'], input_func=lambda _: '0', output=output)
        rendered = output.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn('Загружено записей: 12', rendered)

    def test_console_prints_unexpected_errors(self) -> None:
        answers = iter(['6', '0'])
        output = StringIO()

        with patch('hashlab.presentation.console._handle_show_stats', side_effect=RuntimeError('boom')):
            exit_code = main(argv=[], input_func=lambda _: next(answers), output=output)

        self.assertEqual(exit_code, 0)
        self.assertIn('Непредвиденная ошибка: boom', output.getvalue())

    def test_empty_table_rendering_message(self) -> None:
        self.assertEqual(render_table(()), 'Таблица не инициализирована.')

    def test_ask_uses_native_input_when_output_is_stdout(self) -> None:
        with patch('builtins.input', return_value='answer') as input_mock:
            result = _ask(input, sys.stdout, 'prompt: ')

        self.assertEqual(result, 'answer')
        input_mock.assert_called_once_with('prompt: ')


if __name__ == '__main__':
    unittest.main()
