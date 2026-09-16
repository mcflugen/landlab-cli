from __future__ import annotations

import inspect
import re
from collections import defaultdict
from collections.abc import Collection
from collections.abc import Mapping
from typing import Any


def catalog_components(components: dict[str, Any]) -> dict[str, Any]:
    details = {}
    for name, cls in sorted(components.items()):
        details[name] = {
            "name": f"{cls.__module__}.{cls.__name__}",
            "unit_agnostic": cls._unit_agnostic,
            "info": normalize_component_info(cls._info),
            "summary": docstring_summary(cls.__doc__),
        }
    return details


def catalog_component_fields(
    components: Mapping[str, Any],
    *,
    used_by: str | Collection[str] | None = None,
    provided_by: str | Collection[str] | None = None,
) -> dict[str, Any]:
    if isinstance(used_by, str):
        used_by = [used_by]
    if isinstance(provided_by, str):
        provided_by = [provided_by]

    details: dict[str, Any] = defaultdict(lambda: defaultdict(set))
    for name, cls in components.items():
        component_path = f"{cls.__module__}.{cls.__name__}"
        if used_by is None and provided_by is None:
            include_inputs = include_outputs = True
        else:
            include_inputs = used_by is not None and name in used_by
            include_outputs = provided_by is not None and name in provided_by

        for field, desc in cls._info.items():
            is_input = include_inputs and desc["intent"].startswith("in")
            is_output = include_outputs and desc["intent"].endswith("out")

            if not (is_input or is_output):
                continue

            details[field]["desc"].add(desc["doc"])
            if is_input:
                details[field]["used_by"].add(component_path)
            if is_output:
                details[field]["provided_by"].add(component_path)

    return normalize_fields(
        {
            field: info
            for field, info in details.items()
            if (used_by is None or info["used_by"])
            and (provided_by is None or info["provided_by"])
        }
    )


def catalog_grids(grids: dict[str, Any]) -> dict[str, Any]:
    details = {}
    for name, cls in grids.items():
        details[name] = categorize_class(cls)
        details[name]["field-io"] |= {
            f"{cls.__module__}.{cls.__name__}.at_node",
            f"{cls.__module__}.{cls.__name__}.at_link",
            f"{cls.__module__}.{cls.__name__}.at_patch",
            f"{cls.__module__}.{cls.__name__}.at_corner",
            f"{cls.__module__}.{cls.__name__}.at_face",
            f"{cls.__module__}.{cls.__name__}.at_cell",
        }

    return normalize_grids(details)


def select_components(
    components: dict[str, Any],
    *,
    using: Collection[str] | None = None,
    providing: Collection[str] | None = None,
) -> dict[str, Any]:
    if using is None and providing is None:
        return components

    using = set(using) if using is not None else None
    providing = set(providing) if providing is not None else None

    return {
        name: cls
        for name, cls in components.items()
        if (using is None or using & set(cls.input_var_names))
        and (providing is None or providing & set(cls.output_var_names))
    }


def select_components_by_name(
    components: dict[str, Any],
    *,
    names: str | Collection[str] | None = None,
) -> dict[str, Any]:
    if names is None:
        return components

    if isinstance(names, str):
        names = [names]

    return {name: components[name] for name in names}


def normalize_component_info(info: dict[str, Any]) -> dict[str, Any]:
    normed = {}
    for name, desc in sorted(info.items()):
        normed[name] = {
            "doc": desc["doc"],
            "dtype": normalize_field_dtype(desc["dtype"]),
            "intent": desc["intent"],
            "mapping": desc["mapping"],
            "optional": bool(desc["optional"]),
            "units": desc["units"],
        }

    return normed


def normalize_field_dtype(dtype: Any) -> str:
    if isinstance(dtype, type):
        return dtype.__name__
    return str(dtype)


def normalize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    normed = {}
    for field, info in sorted(fields.items()):
        if len(info["desc"]) != 1:
            raise ValueError(field)
        normed[field] = {
            "desc": tuple(info["desc"])[0],
            "used_by": sorted(info["used_by"]),
            "provided_by": sorted(info["provided_by"]),
        }

    return normed


def normalize_grids(grids: dict[str, Any]) -> dict[str, Any]:
    normed = {}

    for name, info in sorted(grids.items()):
        normed[name] = {tag: sorted(values) for tag, values in sorted(info.items())}

    return normed


ALL_TAGS = {
    "boundary-condition",
    "connectivity",
    "deprecated",
    "field-add",
    "field-io",
    "gradient",
    "info-cell",
    "info-corner",
    "info-face",
    "info-field",
    "info-grid",
    "info-link",
    "info-node",
    "info-patch",
    "map",
    "quantity",
    "subset",
    "surface",
    "uncategorized",
}


def categorize_class(cls: type) -> dict[str, set[str]]:
    funcs: dict[str, set[str]] = {tag: set() for tag in ALL_TAGS}

    for name, func in inspect.getmembers(cls):
        if not name.startswith("_"):
            full_name = ".".join([cls.__module__, cls.__name__, name])
            for cat in landlab_metadata(inspect.getdoc(func)):
                funcs[cat].add(full_name)
    return funcs


_LANDLAB_METADATA = re.compile(r"^:meta\s+landlab:\s*(.*)$")


def landlab_metadata(docstring: str | None) -> frozenset[str]:
    if not docstring:
        return frozenset(["uncategorized"])

    tags: set[str] = set()

    for line in inspect.cleandoc(docstring).splitlines():
        match = _LANDLAB_METADATA.match(line)
        if match:
            tags.update(tag.strip() for tag in match.group(1).split(",") if tag.strip())

    return frozenset(tags or ["uncategorized"])


def docstring_summary(docstring: str | None) -> str:
    if not docstring:
        return ""

    cleaned = inspect.cleandoc(docstring)
    return cleaned.partition("\n")[0]
