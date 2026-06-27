"""Shared helper functions."""

from collections.abc import Iterable


def compact_lines(lines: Iterable[str]) -> str:
    """Join non-empty lines with whitespace normalized."""
    return "\n".join(line.strip() for line in lines if line and line.strip())
