from __future__ import annotations

import argparse

from landlab_cli._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="landlab", allow_abbrev=False)
    parser.add_argument(
        "--version", action="version", version=f"landlab-cli {__version__}"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
