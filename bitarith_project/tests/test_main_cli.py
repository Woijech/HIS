import unittest
from unittest.mock import patch

from bitarith import __main__ as app


class TestMainCLI(unittest.TestCase):
    def _run_main(self, inputs):
        with patch("builtins.input", side_effect=inputs), patch("builtins.print") as mocked_print:
            app.main()
            return mocked_print

    def test_readers_reprompt(self):
        with patch("builtins.input", side_effect=["abc", "-13"]), patch("builtins.print"):
            self.assertEqual(app._read_int("n="), -13)

        with patch("builtins.input", side_effect=["...", "-3.25"]), patch("builtins.print"):
            self.assertEqual(app._read_dec_str("x="), "-3.25")

        with patch("builtins.input", side_effect=["-1", "123456789", "1234"]), patch("builtins.print"):
            self.assertEqual(app._read_digits("d="), "1234")

    def test_main_unknown_then_exit(self):
        mocked_print = self._run_main(["42", "0"])
        calls = [str(c.args[0]) for c in mocked_print.call_args_list if c.args]
        self.assertTrue(any("Неизвестный пункт" in s for s in calls))
        self.assertTrue(any("Пока!" in s for s in calls))

    def test_main_arithmetic_paths(self):
        self._run_main(["1", "7", "0"])
        self._run_main(["2", "1", "2", "0"])
        self._run_main(["3", "5", "2", "0"])
        self._run_main(["4", "-7", "6", "0"])
        self._run_main(["5", "1", "2", "0"])

    def test_main_ieee_and_bcd_paths(self):
        self._run_main(["6", "%", "0"])
        self._run_main(["6", "+", "1.5", "2.25", "0"])
        self._run_main(["7", "1234", "66", "0"])


if __name__ == "__main__":
    unittest.main()
