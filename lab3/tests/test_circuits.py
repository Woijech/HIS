import os
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import circuits
import constants

SCHEMA_ROOT = Path(ROOT) / "schema"


def eval_expr(expr: str, mapping: dict[str, bool]) -> bool:
    """Evaluate a minimized boolean expression against a variable mapping."""

    expr = expr.strip()
    if expr == "1":
        return True
    if expr == "0" or expr == "":
        return False
    expr = expr.replace("!", " not ")
    expr = expr.replace("&", " and ")
    expr = expr.replace("|", " or ")
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
    for token in sorted(tokens, key=len, reverse=True):
        if token in {"and", "or", "not"}:
            continue
        expr = re.sub(rf"\b{token}\b", f"mapping['{token}']", expr)
    return bool(eval(expr, {"__builtins__": {}}, {"mapping": mapping}))


class TestCircuits(unittest.TestCase):
    def test_decode_encode_8421(self):
        for v in range(10):
            enc = circuits.encode_8421(v)
            self.assertEqual(enc, v)
            dec, ok = circuits.decode_8421(enc)
            self.assertTrue(ok)
            self.assertEqual(dec, v)

        for v in range(10, 16):
            dec, ok = circuits.decode_8421(v)
            self.assertFalse(ok)
            self.assertEqual(dec, -1)

        self.assertEqual(circuits.encode_8421(-1), 0)
        self.assertEqual(circuits.encode_8421(15), 0)

    def test_subtractor_equations(self):
        eqs = circuits.get_subtractor_equations()
        self.assertEqual(len(eqs), 2)
        self.assertTrue(eqs[0].sdnf)
        self.assertTrue(eqs[1].sdnf)

        d_minterms = {1, 2, 4, 7}
        b_minterms = {1, 2, 3, 7}
        names = {"d": d_minterms, "b": b_minterms}

        for eq in eqs:
            if eq.name.startswith("d"):
                expected = names["d"]
            else:
                expected = names["b"]
            for value in range(8):
                mapping = {
                    "X1": bool((value >> 2) & 1),
                    "X2": bool((value >> 1) & 1),
                    "X3": bool(value & 1),
                }
                got = eval_expr(eq.minimized, mapping)
                self.assertEqual(got, value in expected)

    def test_decoder_equations(self):
        eqs = circuits.get_decoder_8421_equations()
        self.assertEqual(len(eqs), 4)
        eq_map = {eq.name: eq.minimized for eq in eqs}

        for i in range(10):
            mapping = {
                "I3": bool((i >> 3) & 1),
                "I2": bool((i >> 2) & 1),
                "I1": bool((i >> 1) & 1),
                "I0": bool(i & 1),
            }
            for bit, name in enumerate(["O0", "O1", "O2", "O3"]):
                expected = bool((i >> bit) & 1)
                got = eval_expr(eq_map[name], mapping)
                self.assertEqual(got, expected)

    def test_adder_equations(self):
        eqs = circuits.get_bcd_adder_equations()
        self.assertEqual(len(eqs), 5)
        eq_map = {eq.name: eq.minimized for eq in eqs}

        for a in range(10):
            for b in range(10):
                s = a + b
                mapping = {
                    "A3": bool((a >> 3) & 1),
                    "A2": bool((a >> 2) & 1),
                    "A1": bool((a >> 1) & 1),
                    "A0": bool(a & 1),
                    "B3": bool((b >> 3) & 1),
                    "B2": bool((b >> 2) & 1),
                    "B1": bool((b >> 1) & 1),
                    "B0": bool(b & 1),
                }
                expected = {
                    "S4": bool(s & 16),
                    "S3": bool(s & 8),
                    "S2": bool(s & 4),
                    "S1": bool(s & 2),
                    "S0": bool(s & 1),
                }
                for name, exp in expected.items():
                    got = eval_expr(eq_map[name], mapping)
                    self.assertEqual(got, exp)

    def _check_encoder(self, offset: int) -> None:
        eqs = circuits.get_encoder_8421_equations(offset)
        self.assertEqual(len(eqs), 8)
        eq_map = {eq.name: eq.minimized for eq in eqs}

        for i in range(19):
            mapping = {
                "S4": bool((i >> 4) & 1),
                "S3": bool((i >> 3) & 1),
                "S2": bool((i >> 2) & 1),
                "S1": bool((i >> 1) & 1),
                "S0": bool(i & 1),
            }
            shifted_value = i + offset
            tens = shifted_value // 10
            units = shifted_value % 10
            tens_bcd = circuits.encode_8421(tens)
            units_bcd = circuits.encode_8421(units)
            expected = {
                "T3": bool(tens_bcd & 8),
                "T2": bool(tens_bcd & 4),
                "T1": bool(tens_bcd & 2),
                "T0": bool(tens_bcd & 1),
                "U3": bool(units_bcd & 8),
                "U2": bool(units_bcd & 4),
                "U1": bool(units_bcd & 2),
                "U0": bool(units_bcd & 1),
            }
            for output_name, expected_value in expected.items():
                got = eval_expr(eq_map[output_name], mapping)
                self.assertEqual(got, expected_value)

    def test_encoder_equations_offset_n(self):
        self._check_encoder(constants.OFFSET_N)
        eqs = circuits.get_encoder_8421_equations_offset_n()
        self.assertEqual(len(eqs), 8)

    def test_counter_equations(self):
        eqs = circuits.get_counter_equations()
        self.assertEqual(len(eqs), 4)
        eq_map = {eq.name: eq.minimized for eq in eqs}

        for state_value in range(constants.COUNTER_MAX_STATE):
            mapping = {
                "Q3": bool((state_value >> 3) & 1),
                "Q2": bool((state_value >> 2) & 1),
                "Q1": bool((state_value >> 1) & 1),
                "Q0": bool(state_value & 1),
            }
            next_state = (
                state_value - 1 + constants.COUNTER_MAX_STATE
            ) % constants.COUNTER_MAX_STATE
            toggle_bits = state_value ^ next_state
            expected = {
                "T3": bool((toggle_bits >> 3) & 1),
                "T2": bool((toggle_bits >> 2) & 1),
                "T1": bool((toggle_bits >> 1) & 1),
                "T0": bool(toggle_bits & 1),
            }
            for output_name, expected_value in expected.items():
                got = eval_expr(eq_map[output_name], mapping)
                self.assertEqual(got, expected_value)

    def test_8421_schema_uses_project_offset(self) -> None:
        schema_path = SCHEMA_ROOT / "8421.circ"
        tree = ET.parse(schema_path)
        constant_values: list[tuple[str | None, str | None]] = []

        for component in tree.iter("comp"):
            if component.attrib.get("name") != "Constant":
                continue

            value = None
            width = None
            for attribute in component.findall("a"):
                if attribute.attrib.get("name") == "value":
                    value = attribute.attrib.get("val")
                if attribute.attrib.get("name") == "width":
                    width = attribute.attrib.get("val")
            constant_values.append((value, width))

        expected_offset = f"0x{constants.OFFSET_N:x}"
        self.assertIn((expected_offset, "5"), constant_values)
        self.assertNotIn(("0x9", "5"), constant_values)
