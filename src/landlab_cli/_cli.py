from __future__ import annotations

import argparse

from landlab_cli._commands import cmd_catalog
from landlab_cli._commands import cmd_components
from landlab_cli._commands import cmd_fields
from landlab_cli._commands import cmd_grids
from landlab_cli._commands import cmd_info
from landlab_cli._landlab import LandlabNotFoundError
from landlab_cli._output import print_error
from landlab_cli._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="landlab-cli", allow_abbrev=False)
    parser.add_argument(
        "--version", action="version", version=f"landlab-cli {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    info_parser = subparsers.add_parser("info")
    info_parser.add_argument("--json", action="store_true")
    info_parser.set_defaults(func=cmd_info)

    components_parser = subparsers.add_parser("components")
    filters = components_parser.add_mutually_exclusive_group()
    filters.add_argument(
        "--using", metavar="FIELD", help="select components that use FIELD"
    )
    filters.add_argument(
        "--providing", metavar="FIELD", help="select components that provide FIELD"
    )
    components_parser.add_argument("--details", action="store_true")
    components_parser.set_defaults(func=cmd_components)

    fields_parser = subparsers.add_parser("fields")
    fields_filters = fields_parser.add_mutually_exclusive_group()
    fields_filters.add_argument(
        "--used-by",
        metavar="COMPONENT",
        help="select fields that are used by COMPONENT",
    )
    fields_filters.add_argument(
        "--provided-by",
        metavar="COMPONENT",
        help="select fields that are provided by COMPONENT",
    )
    fields_parser.add_argument("--details", action="store_true")
    fields_parser.set_defaults(func=cmd_fields)

    grids_parser = subparsers.add_parser("grids")
    grids_parser.add_argument("--details", action="store_true")
    grids_parser.set_defaults(func=cmd_grids)

    catalog_parser = subparsers.add_parser("catalog")
    catalog_parser.set_defaults(func=cmd_catalog)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        try:
            return args.func(args)
        except LandlabNotFoundError as error:
            print_error(f"{parser.prog}: {error}")
            return 1
    else:
        parser.print_help()
    return 0
