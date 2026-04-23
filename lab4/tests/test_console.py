from __future__ import annotations

from io import StringIO
import unittest

from hashlab.presentation.console import main


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


if __name__ == '__main__':
    unittest.main()
