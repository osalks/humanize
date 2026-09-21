from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pytest

import humanize


@pytest.mark.parametrize(
    "test_args, expected",
    [
        ([["1", "2", "3"]], "1, 2 and 3"),
        ([["one", "two", "three"]], "one, two and three"),
        ([["one", "two"]], "one and two"),
        ([["one"]], "one"),
        ([[]], ""),
        ([[""]], ""),
        ([[1, 2, 3]], "1, 2 and 3"),
        ([[1, "two"]], "1 and two"),
        ([("one", "two", "three")], "one, two and three"),
        ([("one", "two")], "one and two"),
        ([("one",)], "one"),
        ([{"one": 1, "two": 2}.keys()], "one and two"),
        ([(x for x in ["one", "two", "three"])], "one, two and three"),
        ([range(1, 4)], "1, 2 and 3"),
    ],
)
def test_natural_list(test_args: Iterable[Any], expected: str) -> None:
    assert humanize.natural_list(*test_args) == expected


@pytest.mark.parametrize(
    ("items", "conjunction", "expected"),
    [
        (["one", "two", "three"], "or", "one, two or three"),
        (["one", "two"], "or", "one or two"),
        (["one"], "or", "one"),
        ([], "or", ""),
        (["one", "two"], "and", "one and two"),
    ],
)
def test_natural_list_conjunction(
    items: Iterable[Any], conjunction: str, expected: str
) -> None:
    """natural_list honours the ``conjunction`` parameter (issue #214)."""
    assert humanize.natural_list(items, conjunction=conjunction) == expected


def test_natural_list_conjunction_invalid() -> None:
    """A conjunction other than 'and'/'or' is rejected."""
    with pytest.raises(ValueError, match="conjunction must be"):
        humanize.natural_list(["one", "two"], conjunction="xor")
