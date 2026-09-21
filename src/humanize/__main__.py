"""Command-line interface for humanize (issue #184).

Exposes the public formatting helpers as a tiny dispatcher:

```console
$ humanize naturalsize 8589934592
8.6 GB
$ humanize naturalsize --binary 8589934592
8.0 GiB
$ echo 8589934592 | humanize naturalsize --format %.3f
8.590 GB
$ python -m humanize intcomma 1234567
1,234,567
```

Positional arguments are coerced to ``int`` or ``float`` when possible and
otherwise passed as strings (e.g. dates for ``naturalday``). ``--flag`` passes
``True``; ``--key value`` passes the coerced value. ``natural_list`` treats all
positional arguments as list items. When no positional value is given and
standard input is not a terminal, the value is read from stdin.
"""

from __future__ import annotations

import argparse
import inspect
import sys

import humanize

_FUNCTIONS = frozenset(
    {
        "apnumber",
        "clamp",
        "fractional",
        "intcomma",
        "intword",
        "metric",
        "natural_list",
        "naturaldate",
        "naturalday",
        "naturaldelta",
        "naturalsize",
        "naturaltime",
        "ordinal",
        "precisedelta",
        "scientific",
    }
)


def _coerce(token: str) -> object:
    """Coerce a CLI token to int/float when possible, else keep the string."""
    for conv in (int, float):
        try:
            return conv(token)
        except ValueError:
            continue
    return token


def _parse_extra(
    tokens: list[str], func: object
) -> tuple[list[object], dict[str, object]]:
    """Split remaining tokens into positional args and ``--key`` kwargs.

    ``--key=value`` always passes a coerced value; ``--key value`` consumes the
    next token only when the function's matching parameter is not a bool flag
    (or when the key is unknown); a bare ``--flag`` passes ``True``.
    """
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        params = {}
    args: list[object] = []
    kwargs: dict[str, object] = {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("--"):
            key_value = token[2:]
            if "=" in key_value:
                key, _, raw = key_value.partition("=")
                kwargs[key.replace("-", "_")] = _coerce(raw)
            else:
                key = key_value.replace("-", "_")
                param = params.get(key)
                is_flag = isinstance(param.default, bool) if param else False
                if (
                    not is_flag
                    and i + 1 < len(tokens)
                    and not tokens[i + 1].startswith("--")
                ):
                    kwargs[key] = _coerce(tokens[i + 1])
                    i += 1
                else:
                    kwargs[key] = True
        else:
            args.append(_coerce(token))
        i += 1
    return args, kwargs


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``humanize`` console script and ``-m`` invocation."""
    parser = argparse.ArgumentParser(
        prog="humanize",
        description="Format values for humans, from the command line.",
    )
    parser.add_argument("function", choices=sorted(_FUNCTIONS))
    ns, rest = parser.parse_known_args(argv)

    func = getattr(humanize, ns.function)
    args, kwargs = _parse_extra(rest, func)
    if ns.function == "natural_list":
        func_args: list[object] = [args]
    elif not args and not sys.stdin.isatty():
        stdin_tokens = sys.stdin.read().split()
        func_args = [_coerce(token) for token in stdin_tokens]
    else:
        func_args = args

    try:
        result = func(*func_args, **kwargs)
    except (TypeError, ValueError, OverflowError) as exc:
        parser.exit(2, f"humanize: error: {exc}\n")
    if isinstance(result, (list, tuple)):
        result = " ".join(str(item) for item in result)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
