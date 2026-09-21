"""Tests for the command-line interface (issue #184)."""

from __future__ import annotations

import subprocess
import sys

import pytest

import humanize.__main__ as cli


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "humanize", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("naturalsize", "8589934592"), "8.6 GB"),
        (("naturalsize", "--binary", "8589934592"), "8.0 GiB"),
        (("intcomma", "1234567"), "1,234,567"),
        (("ordinal", "5"), "5th"),
        (("intword", "12345591313"), "12.3 billion"),
        (("apnumber", "4"), "four"),
        (("metric", "1500"), "1.50 k"),
        (("naturalday", "today"), "today"),
    ],
)
def test_cli_functions(args: tuple[str, ...], expected: str) -> None:
    proc = run_cli(*args)
    assert proc.returncode == 0
    assert proc.stdout.strip() == expected


def test_cli_format_flag() -> None:
    proc = run_cli("naturalsize", "--format", "%.3f", "8589934592")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "8.590 GB"


def test_cli_natural_list() -> None:
    proc = run_cli("natural_list", "foo", "bar", "baz")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "foo, bar and baz"


def test_cli_reads_stdin() -> None:
    proc = run_cli("naturalsize", stdin="8589934592\n")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "8.6 GB"


def test_cli_unknown_function() -> None:
    proc = run_cli("not_a_function", "1")
    assert proc.returncode != 0
    assert "invalid choice" in proc.stderr


def test_cli_bad_value() -> None:
    proc = run_cli("naturalsize", "not_a_number")
    assert proc.returncode == 2
    assert "error" in proc.stderr


def test_main_direct_call(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["intcomma", "1234"]) == 0
    assert capsys.readouterr().out.strip() == "1,234"
