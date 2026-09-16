import argparse
import platform
import sys

from landlab_cli._catalog import catalog_component_fields
from landlab_cli._catalog import catalog_components
from landlab_cli._catalog import catalog_grids
from landlab_cli._catalog import select_components
from landlab_cli._catalog import select_components_by_name
from landlab_cli._landlab import get_components
from landlab_cli._landlab import get_grids
from landlab_cli._landlab import get_landlab_info
from landlab_cli._output import print_document
from landlab_cli._output import print_error
from landlab_cli._output import print_lines
from landlab_cli._version import __version__


def cmd_info(args: argparse.Namespace) -> int:
    landlab_info = get_landlab_info()

    info = {
        "landlab-cli": {"version": __version__},
        "landlab": {
            "version": landlab_info.version,
            "location": landlab_info.location,
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
    }

    print_document(info, fmt=args.format)

    return 0


def cmd_components(args: argparse.Namespace) -> int:
    selected = select_components(
        get_components(),
        using=args.using,
        providing=args.providing,
    )

    if not args.details and args.format is None:
        print_lines(sorted(selected))
        return 0

    catalog = catalog_components if args.details else sorted

    print_document({"components": catalog(selected)}, fmt=args.format or "toml")

    return 0


def cmd_fields(args: argparse.Namespace) -> int:
    if args.used_by is None and args.provided_by is None:
        component_names = None
    else:
        component_names = set()
        if args.used_by:
            component_names |= set(args.used_by)
        if args.provided_by:
            component_names |= set(args.provided_by)

    try:
        selected = select_components_by_name(get_components(), names=component_names)
    except KeyError as error:
        print_error(f"{error.args[0]}: unknown component")
        return 1

    details = catalog_component_fields(
        selected, used_by=args.used_by, provided_by=args.provided_by
    )

    if not args.details and args.format is None:
        print_lines(sorted(details))
        return 0

    output = details if args.details else sorted(details)

    print_document({"fields": output}, fmt=args.format or "toml")

    return 0


def cmd_grids(args: argparse.Namespace) -> int:
    grids = get_grids()

    if not args.details and args.format is None:
        print_lines(sorted(grids))
        return 0

    catalog = catalog_grids if args.details else sorted

    print_document({"grids": catalog(grids)}, fmt=args.format or "toml")

    return 0


def cmd_catalog(args: argparse.Namespace) -> int:
    components = get_components()
    grids = get_grids()

    doc = {
        "components": catalog_components(components),
        "fields": catalog_component_fields(components),
        "grids": catalog_grids(grids),
    }

    print_document(doc, fmt=args.format)

    return 0
