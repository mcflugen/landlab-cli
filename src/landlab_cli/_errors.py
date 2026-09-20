from __future__ import annotations


class LandlabCLIError(RuntimeError):
    pass


class LandlabNotFoundError(ModuleNotFoundError, LandlabCLIError):
    pass


class LandlabVersionError(LandlabCLIError):
    pass


class ModelLoadError(LandlabCLIError):
    pass


class ModelNotFoundError(ModelLoadError):
    pass


class MissingModelError(ModelLoadError):
    pass


class AmbiguousModelError(ModelLoadError):
    pass


class ModelConfigurationError(LandlabCLIError):
    pass
