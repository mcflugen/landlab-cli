from __future__ import annotations

import json
import sys
from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from typing import Any

import tomli_w


def print_error(msg: str) -> None:
    print(msg, file=sys.stderr)


def print_lines(lines: Iterable[str]) -> None:
    output = "\n".join(lines)
    if output:
        print(output)


def print_document(doc: dict[str, Any], *, fmt: str = "toml") -> None:
    writers: dict[str, Callable[[dict[str, Any]], str]] = {
        "json": partial(json.dumps, indent=2),
        "toml": partial(tomli_w.dumps, indent=2),
    }
    if fmt not in writers:
        raise ValueError("fmt must be one of {', '.join(sorted(writers))}")

    output = writers[fmt](doc)
    if output:
        print(output)
