"""Shared data structures for boolean equations and implicants."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BooleanEquation:
    """A boolean equation in canonical and minimized form."""

    label: str
    canonical_sop: str
    minimized_expression: str

    @property
    def name(self) -> str:
        """Backward-compatible alias for the equation label."""

        return self.label

    @property
    def sdnf(self) -> str:
        """Backward-compatible alias for the canonical sum-of-products form."""

        return self.canonical_sop

    @property
    def minimized(self) -> str:
        """Backward-compatible alias for the minimized expression."""

        return self.minimized_expression


@dataclass(frozen=True, slots=True)
class ImplicantTerm:
    """A boolean implicant described by its fixed bits and wildcard mask."""

    bit_pattern: int
    wildcard_mask: int

    @property
    def value(self) -> int:
        """Backward-compatible alias for the stored bit pattern."""

        return self.bit_pattern

    @property
    def mask(self) -> int:
        """Backward-compatible alias for the wildcard mask."""

        return self.wildcard_mask

    def is_equal(self, other: "ImplicantTerm") -> bool:
        """Return True when two implicants describe the same term."""

        return self == other

    def matches(self, minterm_value: int) -> bool:
        """Return True when the implicant covers the provided minterm."""

        return (minterm_value & ~self.wildcard_mask) == (
            self.bit_pattern & ~self.wildcard_mask
        )

    def covers(self, minterm_value: int) -> bool:
        """Backward-compatible alias for :meth:`matches`."""

        return self.matches(minterm_value)
