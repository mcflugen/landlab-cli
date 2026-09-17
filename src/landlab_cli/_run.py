import inspect
import pathlib
import runpy
from typing import Any

from landlab_cli._errors import AmbiguousModelError
from landlab_cli._errors import MissingModelError
from landlab_cli._errors import ModelConfigurationError
from landlab_cli._errors import ModelLoadError
from landlab_cli._errors import ModelNotFoundError
from landlab_cli._landlab import load_landlab


def load_model(path: str, *, name: str | None = None) -> type[Any]:
    load_landlab("landlab", min_version="2.11.1.dev0")

    models = load_model_classes(path)
    if name is not None and name not in models:
        raise MissingModelError(f"{name} not in {path}")

    if len(models) == 0:
        raise ModelNotFoundError(f"no models found in {path}")

    if len(models) > 1 and name is None:
        raise AmbiguousModelError(f"multiple models found in {path}")

    if name is None:
        return list(models.values())[0]

    return models[name]


def load_model_config(config: str) -> dict[str, Any]:
    load_landlab("landlab", min_version="2.11.1.dev0")

    from landlab.core.model_parameter_loader import ConfigurationError
    from landlab.core.model_parameter_loader import load_params

    try:
        params = load_params(pathlib.Path(config))
    except ConfigurationError as error:
        raise ModelConfigurationError(str(error)) from error

    return params


def load_model_classes(path: str) -> dict[str, type]:
    try:
        with open(path):
            pass
    except OSError as error:
        raise ModelLoadError(str(error))

    namespace = runpy.run_path(path)
    return {
        name: obj
        for name, obj in namespace.items()
        if is_model_class(obj)
        and obj.__module__ == namespace["__name__"]
        and not inspect.isabstract(obj)
    }


def is_model_class(obj: Any) -> bool:
    model_cls = load_landlab("landlab.core.model").Model

    return inspect.isclass(obj) and issubclass(obj, model_cls) and obj is not model_cls
