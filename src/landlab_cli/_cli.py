from __future__ import annotations

import argparse

from landlab_cli._commands import cmd_catalog
from landlab_cli._commands import cmd_components
from landlab_cli._commands import cmd_fields
from landlab_cli._commands import cmd_grids
from landlab_cli._commands import cmd_info
from landlab_cli._commands import cmd_lint
from landlab_cli._commands import cmd_run
from landlab_cli._errors import LandlabCLIError
from landlab_cli._output import print_error
from landlab_cli._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="landlab-cli", allow_abbrev=False)
    parser.add_argument(
        "--version", action="version", version=f"landlab-cli {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    info_parser = subparsers.add_parser("info")
    info_parser.add_argument(
        "--format",
        choices=("toml", "json"),
        default="toml",
        help="output format",
    )
    info_parser.set_defaults(func=cmd_info)

    components_parser = subparsers.add_parser("components")
    components_parser.add_argument(
        "--using",
        metavar="FIELD",
        action="append",
        help="select components that use FIELD",
    )
    components_parser.add_argument(
        "--providing",
        metavar="FIELD",
        action="append",
        help="select components that provide FIELD",
    )
    components_parser.set_defaults(func=cmd_components)

    fields_parser = subparsers.add_parser("fields")
    fields_parser.add_argument(
        "--used-by",
        metavar="COMPONENT",
        action="append",
        help="select fields that are used by COMPONENT",
    )
    fields_parser.add_argument(
        "--provided-by",
        metavar="COMPONENT",
        action="append",
        help="select fields that are provided by COMPONENT",
    )
    fields_parser.set_defaults(func=cmd_fields)

    grids_parser = subparsers.add_parser("grids")
    grids_parser.set_defaults(func=cmd_grids)

    for _parser in (components_parser, fields_parser, grids_parser):
        _parser.add_argument("--details", action="store_true")
        _parser.add_argument(
            "--format",
            choices=("toml", "json"),
            default=None,
            help="output format",
        )

    catalog_parser = subparsers.add_parser("catalog")
    catalog_parser.add_argument(
        "--format",
        choices=("toml", "json"),
        default="toml",
        help="output format",
    )
    catalog_parser.set_defaults(func=cmd_catalog)

    lint_parser = subparsers.add_parser("lint")
    lint_parser.add_argument("--exclude", action="append", help="issues to ignore")
    lint_parser.add_argument(
        "--format",
        choices=("text", "json", "toml"),
        default="text",
        help="output format",
    )
    lint_parser.set_defaults(func=cmd_lint)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("module")
    run_parser.add_argument("--config", metavar="PATH", default=None)
    run_parser.add_argument("--model", metavar="NAME", default=None)
    run_parser.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        try:
            return args.func(args)
        except LandlabCLIError as error:
            print_error(f"{parser.prog}: {error}")
            return 1
    else:
        parser.print_help()
    return 0
