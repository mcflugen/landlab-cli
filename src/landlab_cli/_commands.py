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

    print_document(info, fmt="json" if args.json else "toml")

    return 0


def cmd_components(args: argparse.Namespace) -> int:
    selected = select_components(
        get_components(),
        using=args.using,
        providing=args.providing,
    )

    if not args.details:
        print_lines(sorted(selected))
        return 0

    details = catalog_components(selected)

    print_document({"components": details}, fmt="toml")

    return 0


def cmd_fields(args: argparse.Namespace) -> int:
    component_name = args.used_by if args.used_by is not None else args.provided_by

    try:
        selected = select_components_by_name(get_components(), names=component_name)
    except KeyError as error:
        print_error(f"{error.args[0]}: unknown component")
        return 1

    include_inputs = args.provided_by is None
    include_outputs = args.used_by is None

    details = catalog_component_fields(
        selected.values(),
        include_inputs=include_inputs,
        include_outputs=include_outputs,
    )

    if not args.details:
        print_lines(sorted(details))
        return 0

    print_document({"fields": details})
    return 0


def cmd_grids(args: argparse.Namespace) -> int:
    grids = get_grids()

    if not args.details:
        print_lines(sorted(grids))
        return 0

    index = catalog_grids(grids)

    print_document({"grids": index})

    return 0


def cmd_catalog(args: argparse.Namespace) -> int:
    components = get_components()
    grids = get_grids()

    doc = {
        "components": catalog_components(components),
        "fields": catalog_component_fields(components.values()),
        "grids": catalog_grids(grids),
    }

    print_document(doc, fmt="toml")

    return 0
