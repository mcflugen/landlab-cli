from __future__ import annotations

import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from packaging.version import Version

from landlab_cli._errors import LandlabNotFoundError
from landlab_cli._errors import LandlabVersionError


@dataclass(frozen=True)
class LandlabInfo:
    version: str
    location: str


def load_landlab(name: str, *, min_version: str | None = None) -> ModuleType:
    if min_version is not None:
        version = Version(_load_landlab("landlab._version").__version__)
        if version < Version(min_version):
            raise LandlabVersionError(f"landlab version must be >= {min_version}")

    return _load_landlab(name)


def _load_landlab(name: str) -> ModuleType:
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError as err:
        if err.name == "landlab":
            raise LandlabNotFoundError("landlab is not installed") from None
        raise
    return module


def get_landlab_info() -> LandlabInfo:
    try:
        version = load_landlab("landlab._version").__version__
        location = load_landlab("landlab").__file__
    except LandlabNotFoundError:
        version = "not installed"
        location = "not installed"

    if location is None:
        location = "unknown"

    return LandlabInfo(version=version, location=location)


def get_components() -> dict[str, type[Any]]:
    component_list = tuple(load_landlab("landlab.components").COMPONENTS)
    base_class = load_landlab("landlab.core.model_component").Component

    return {cls.__name__: cls for cls in component_list if issubclass(cls, base_class)}


def get_grids() -> dict[str, Any]:
    landlab = load_landlab("landlab")
    return {
        name: getattr(landlab, name)
        for name in landlab.__all__
        if name.endswith("Grid")
    }
